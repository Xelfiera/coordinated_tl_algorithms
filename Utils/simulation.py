import traci
import os

cur_phase_duration = 0
sub_range = 50  # calculation range for max_pressure and webster
tmin = 6  # minimum green time for max_pressure and webster

def start():
    sim_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Network")
    sim_file = fr"{sim_path}\kilis.sumocfg"
    traci.start([
        "sumo-gui", "-c", f"{sim_file}", '--start', '--quit-on-end'
    ])