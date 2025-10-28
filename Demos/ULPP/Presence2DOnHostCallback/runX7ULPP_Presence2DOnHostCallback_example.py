import sys
import numpy as np
from Presence2DPlotter.Presence2DHelper import Presence2DHelper

from presence2DOnHost_callback import Presence2DOnHostCallback

def example_presence2D_callback( presence2DHelper: Presence2DHelper):
    

    print("Seq.Num: ", presence2DHelper.get_sequence_number())
    print("Timestamp: ", presence2DHelper.get_timestamp())
    print("Time since start: ", presence2DHelper.get_time_since_start())
    print("Presence State: ", presence2DHelper.get_presence_state())
    print("X, Y Position: ", presence2DHelper.get_x_meters(), ", ", presence2DHelper.get_y_meters())
    print("Confidence: ", presence2DHelper.get_confidence())

    # Return True to continue processing, False to stop the flow
    return True

if __name__ == "__main__":

    if len(sys.argv) > 1:
        setup_json = sys.argv[1]


        Presence2DOnHostCallback().run_with_callback_preset(example_presence2D_callback,
            setup_json)

    else:
        print("Usage: python runX7ULPP_Presence2DOnHostCallback_example.py <path-to-setup.json>")
