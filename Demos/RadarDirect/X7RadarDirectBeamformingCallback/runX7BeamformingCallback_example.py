import sys
import numpy as np

from RadarDirectBeamCallbackRunner import RadarDirectBeamCallback, RadarDirectBeamHelper

def example_radar_direct_beam_callback(rd_beams: np.ndarray, sequence_num: int, 
                           timestamp: int, rd_helper: RadarDirectBeamHelper):
    
    range_vec = rd_helper.get_range_vector()
    azimuths = rd_helper.get_azimuth_angles()
    
    # angle azimuths[N] corresponds to RD matrix rd_beams[N]
    print("Shape of data matrix for angle ", azimuths[0], " : ", rd_beams[0].shape)
    print(f"RangeVec lims: {range_vec[0]:.2f} m to {range_vec[-1]:.2f} m")
    print(f"Timestamp: {timestamp}, Sequence number: {sequence_num}")

    # Return True to continue processing, False to stop the flow
    return False

if __name__ == "__main__":

    if len(sys.argv) > 1:
        setup_json = sys.argv[1]

        RadarDirectBeamCallback().run_with_callback_preset(example_radar_direct_beam_callback, 
            setup_json)

    else:
        print("Usage: python runX7BeamformingCallback_example.py <path-to-setup.json>")
