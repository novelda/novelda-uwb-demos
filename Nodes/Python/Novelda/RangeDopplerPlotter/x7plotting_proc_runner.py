from __future__ import annotations

import os
import sys

from pyqtgraph.Qt import QtCore
QTimer = QtCore.QTimer

from Utils.sharedmem_handler import SharedMemReceiver
from RangeDopplerPlotter.RangeDopplerPlotter_plotter import RangeDopplerPlotter

def main_loop(sharedmem: SharedMemReceiver, plotter: RangeDopplerPlotter, 
              close_path: str, poll_timer):

    if not os.path.exists(close_path):
        poll_timer.stop()
        sharedmem.cleanup()
        return
        # done with receiving data

    while sharedmem.check_data_ready():
        data = sharedmem.read_objdata()
        plotter.receive_data(data)

    plotter.update()


if __name__ == "__main__":
    shm_name       = sys.argv[1]
    shm_blocksize  = sys.argv[2]
    shm_blockcount = sys.argv[3]
    close_path     = sys.argv[4]

    sharedmem = SharedMemReceiver(
        shm_name=shm_name,
        block_size=shm_blocksize,
        num_blocks=shm_blockcount,
        verbose=False
        )

    plotter = RangeDopplerPlotter(shm_on_exit=sharedmem.cleanup)
    plotter.init_window()
    print("PLOTTING_PROCESS_READY", flush=True)

    if sharedmem.check_data_ready(): # for the params dict
        data = sharedmem.read_objdata()
        plotter.receive_data(data)

    poll_timer = QTimer(plotter.mainwin)
    poll_timer.timeout.connect(lambda: main_loop(sharedmem, plotter, close_path, poll_timer))

    UPDATE_FREQ = 40
    started = poll_timer.start(1000 / UPDATE_FREQ)

    # Start event loop (blocking)
    plotter.start_event_loop()
