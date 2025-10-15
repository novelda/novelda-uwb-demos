import sys
import numpy as np

from RDBeamCallbackRunner import RDBeamformingCallback, RangeDopplerBeamHelper

def example_beam_rd_callback(rd_beams: np.ndarray, sequence_num: int, 
                           timestamp: int, rd_helper: RangeDopplerBeamHelper):
    
    range_vec = rd_helper.get_range_vector()
    doppler_vec = rd_helper.get_doppler_vector()
    azimuths = rd_helper.get_azimuth_angles()
    
    # angle azimuths[N] corresponds to RD matrix rd_beams[N]
    print("Shape of RD matrix for angle ", azimuths[0], " : ", rd_beams[0].shape)

    # Return True to continue processing, False to stop the flow
    return False

if __name__ == "__main__":

    if len(sys.argv) > 1:
        setup_json = sys.argv[1]

        RDBeamformingCallback().run_with_callback_preset(example_beam_rd_callback, 
            setup_json)

    else:
        print("Usage: python runX7RDBeamformingCallback_example.py <path-to-setup.json>")
