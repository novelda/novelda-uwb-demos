import sys
import numpy as np

from radar_direct_callback import RadarDirectCallback

def example_radar_callback(trx_vec: np.ndarray, radar_data: np.ndarray, sequence_num: int, 
                           timestamp: int, range_offset: float, bin_length: float):
    
    # range_offset and bin_length are constants

    print("Seq.Num: ", sequence_num)
    print("Timestamp: ", timestamp)
    print("TrxVec: ", trx_vec)
    print("Got data with shape: ", radar_data.shape)

    # Return True to continue processing, False to stop the flow
    return True

if __name__ == "__main__":

    if len(sys.argv) > 1:
        setup_json = sys.argv[1]

        RadarDirectCallback().run_with_callback_preset(example_radar_callback, 
            setup_json)

    else:
        print("Usage: python runX7RadarDirectCallback_example.py <path to preset json>")
