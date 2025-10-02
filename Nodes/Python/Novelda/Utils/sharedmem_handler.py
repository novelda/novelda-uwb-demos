from __future__ import annotations

import pickle
import time
import os
from pathlib import Path
from multiprocessing import shared_memory, resource_tracker
import numpy as np
import json

SHS = 4 # size of size header
THS = SHS + 1 # total header size

# for cleaning up possible mem leaks in case the process is killed abruptly
REG_FILE = str(Path(__file__).resolve().parent / "logs" / "sharedmem_reg.txt")

# cant have several instances of this running, the last one will pick up
# sharedmem_reg.txt and kill any shared memory before it
# but better to be safe than sorry, it seems that on inferior systems (linux, mac)
# the memory stays allocated even after the process ends

class MemBlock:
        """
        0 = available for write
        1 = available for read
        """
        def __init__(self, sharedmem: shared_memory.SharedMemory, start_inx, block_size):
            self.sharedmem = sharedmem
            self.start_inx = start_inx
            self.block_size = block_size
        
        def check_available_for_write(self):
            return self.sharedmem.buf[self.start_inx] == 0
    
        def check_available_for_read(self):
            return self.sharedmem.buf[self.start_inx] == 1
        
        def make_available_write(self):
            self.sharedmem.buf[self.start_inx] = 0
        
        def make_available_read(self):
            self.sharedmem.buf[self.start_inx] = 1
        
        def write_data(self, data: bytes):
            data_size = len(data)

            self.sharedmem.buf[self.start_inx + 1: self.start_inx + THS] = data_size.to_bytes(SHS, byteorder="little")
            self.sharedmem.buf[self.start_inx + THS: self.start_inx + THS + data_size] = data

        def read_data_as_obj(self):
            # Read data size
            size_bytes = self.sharedmem.buf[self.start_inx + 1: self.start_inx + THS]
            data_size = int.from_bytes(size_bytes, byteorder="little")
            
            objdata = pickle.loads(self.sharedmem.buf[self.start_inx + THS: self.start_inx + THS + data_size])
            return objdata
        
        def will_it_fit(self, data_size: int):
            return data_size + THS <= self.block_size


class SharedMemSender:

    def __init__(self, block_size, num_blocks, verbose=True):
        self.block_size = block_size
        self.num_blocks = num_blocks
        self.total_size = block_size * num_blocks
        self.sharedmem = shared_memory.SharedMemory(create=True, size=self.total_size)

        self.verbose = verbose
        self.did_unlink = False

        self.cleanup_stale()

        # save name : time for later cleanup in case this process dies before unlink()
        # also debugging purposes
        reg = {f"{self.sharedmem.name}" : time.time()}
        self.save_registry(reg)

        # Initialize all blocks as available for writing
        for i in range(num_blocks):
            self.sharedmem.buf[i * block_size] = 0

        self.blocks = [MemBlock(self.sharedmem, i * block_size, block_size) for i in range(num_blocks)]
        self.current_block_inx = 0

        self.total_data_dropped = 0
    
    def check_buff_exists(self):
        return self.sharedmem is not None and self.sharedmem.buf is not None
    
    def logthis(self, msg):
        if self.verbose:
            print(msg)
    
    def load_registry(self):
        if not os.path.exists(REG_FILE):
            return {}
        with open(REG_FILE,"r") as f:
            try:
                return json.load(f)
            except Exception as e:
                self.logthis(f"Failed to load shm file{REG_FILE}: {e}")
                return {}

    def save_registry(self, reg):
        os.makedirs(os.path.dirname(REG_FILE), exist_ok=True)
        try:
            with open(REG_FILE, "w") as f:
                json.dump(reg, f)
        except Exception as e:
            self.logthis(f"Failed to save shared memory registry: {e}")

    def cleanup_stale(self):
        reg = self.load_registry()
        removed = []
        for name, ts in reg.items():
            if time.time() - ts < 60*10: # 10 minutes
                continue
            try:
                shm = shared_memory.SharedMemory(name=name)
                shm.close()
                shm.unlink()
                removed.append(name)
            except FileNotFoundError:
                self.logthis("FILENOTFOUND, was already unlinked")

        if len(removed):
            self.logthis(f"Cleaned up {len(removed)} forgotten shared_memory files")

    def advance_block(self):
        self.current_block_inx = (self.current_block_inx + 1) % self.num_blocks

    def send_data(self, pickleable_data, on_not_available=""):

        if not self.check_buff_exists():
            return False

        # check if the proper next block is available
        current_block = self.blocks[self.current_block_inx]
        if not current_block.check_available_for_write():
            self.total_data_dropped += 1
            if on_not_available.lower() == "throw":
                raise MemoryError("Previous data wasn't read, dropping data")
            elif on_not_available.lower() == "print":
                self.logthis(f"Previous data wasn't read, dropping data, total: {self.total_data_dropped}")
                return False
            else:
                return False

        bdata = pickle.dumps(pickleable_data)
         
        data_size = len(bdata)

        # check if data fits
        if not current_block.will_it_fit(data_size):
            raise MemoryError("Data won't fit in block, increase block size")
        
        current_block.write_data(bdata)
        current_block.make_available_read()

        self.advance_block()

        return True

    def are_all_read(self):
        if not self.check_buff_exists():
            return False
        return all(block.check_available_for_write() for block in self.blocks)

    def cleanup(self):
        if self.did_unlink:
            return
        if hasattr(self, 'sharedmem'):
            reg = self.load_registry()
            if self.sharedmem.name in reg:
                del reg[self.sharedmem.name]
                self.save_registry(reg)

            self.sharedmem.close()
            self.sharedmem.unlink()
            self.did_unlink = True
    
    def __del__(self):
        self.cleanup()

class SharedMemReceiver:
    
    def __init__(self, shm_name: str, block_size: int, num_blocks: int, verbose=False):
        self.block_size = int(block_size)
        self.num_blocks = int(num_blocks)
        self.total_size = self.block_size * self.num_blocks
        self.sharedmem = shared_memory.SharedMemory(name=shm_name)
        
        self.blocks = [MemBlock(self.sharedmem, i * self.block_size, self.block_size) for i in range(self.num_blocks)]
        self.current_block_inx = 0
        
        self.verbose = verbose
        self.did_cleanup = False
    
    def check_buff_exists(self):
        return self.sharedmem is not None and self.sharedmem.buf is not None
    
    def advance_block(self):
        self.current_block_inx = (self.current_block_inx + 1) % self.num_blocks
    
    def check_data_ready(self):
        if not self.check_buff_exists():
            return False
        return self.blocks[self.current_block_inx].check_available_for_read()
    
    def read_objdata(self):
        if not self.check_buff_exists():
            return None

        if not self.check_data_ready():
            raise RuntimeError("Data not ready for reading, always check first")

        objdata = self.blocks[self.current_block_inx].read_data_as_obj()
        self.blocks[self.current_block_inx].make_available_write()
        self.advance_block()
        
        return objdata
    
    def cleanup(self):
        if self.did_cleanup:
            return
        self.did_cleanup = True
        self.sharedmem.close()

        # it registers itself on construction even though create=False, python issue,
        # manually unregister if not windows
        if not os.name=="nt":
            resource_tracker.unregister(f"/{self.sharedmem.name}", 'shared_memory')

    def __del__(self):
        self.cleanup()

        

        



        

        
        
        

