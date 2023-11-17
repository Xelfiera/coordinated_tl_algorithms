import traci
from Utils import simulation
from Utils.trafficlight import TrafficLight
import math

update_freq = 600  # webster update frequency
saturation_flow = 0.38  # saturation rate (veh/s), default: 0.38

def websters_method():
    simulation.start()
    traffic_lights = create_tls(traci.trafficlight.getIDList())

    while traci.simulation.getMinExpectedNumber() > 0:
        for tl_id in traffic_lights.keys():
            calc_webster_vehicle_counts(traffic_lights[tl_id])

            if traci.simulation.getTime() % update_freq == 0:
                traffic_lights[tl_id].cycle_green_times = calc_websters_green_times(traffic_lights[tl_id].webster_vehicle_counts)
                traffic_lights[tl_id].webster_vehicle_counts = [0, 0, 0, 0]

            if traffic_lights[tl_id].phase_duration == 0:
                if traffic_lights[tl_id].phase_status == 'g':
                    check_phase_jump(traffic_lights[tl_id])

                    if traffic_lights[tl_id].pre_phase_index != traffic_lights[tl_id].cur_phase_index:
                        set_yellow_phase(traffic_lights[tl_id])
                    else:
                        phase_index = traffic_lights[tl_id].cur_phase_index
                        traffic_lights[tl_id].phase_duration = traffic_lights[tl_id].cycle_green_times[phase_index]

                elif traffic_lights[tl_id].phase_status == 'y':
                    set_green_phase(traffic_lights[tl_id])

            traffic_lights[tl_id].pre_inrange_vehicles = traffic_lights[tl_id].inrange_vehicles
            traffic_lights[tl_id].phase_duration -= 1

        traci.simulationStep()

def create_tls(tl_ids):
    traffic_lights = {}
    for tl_id in tl_ids:
        traffic_lights[tl_id] = TrafficLight(tl_id)
    return traffic_lights

def calc_webster_vehicle_counts(traffic_light):
    tl_position = traci.junction.getPosition(traffic_light.id)
    traffic_light.inrange_vehicles = get_inrange_vehicles(tl_position, traffic_light.inc_edges)
    if traffic_light.pre_inrange_vehicles:
        for i, lane_vehicles in enumerate(traffic_light.pre_inrange_vehicles):
            for vehicle in lane_vehicles:
                if vehicle not in traffic_light.inrange_vehicles[i]:
                    traffic_light.webster_vehicle_counts[i] += 1

def get_inrange_vehicles(tl_pos, edges):
    vehicles_in_range = []
    for edge in edges:
        edge_vehicles = []
        vehicles = traci.edge.getLastStepVehicleIDs(edge)
        if len(vehicles) != 0:
            for vehicle in vehicles:
                pos = traci.vehicle.getPosition(vehicle)
                dist = math.sqrt((tl_pos[0] - pos[0])**2 + (tl_pos[1] - pos[1])**2)
                if dist <= simulation.sub_range:
                    edge_vehicles.append(vehicle)
        vehicles_in_range.append(edge_vehicles)
    return vehicles_in_range

def calc_websters_green_times(v_counts):
    y_crits = []
    for count in v_counts:
        y_crits.append((count / update_freq) / saturation_flow)

    upper_y = sum(y_crits)
    if upper_y > 0.85:
        upper_y = 0.85
    elif upper_y == 0.0:
        upper_y = 0.01

    upper_l = 4 * 2  # 2 seconds yellow for each phases
    upper_c = int(((1.5 * upper_l) + 5) / (1 - upper_y))  # calculate webster's cycle time
    upper_g = upper_c - upper_l  # total green time for cycle

    green_times = []
    for y in y_crits:
        g_time = int((y / upper_y) * upper_g)
        if g_time < simulation.tmin:
            g_time = simulation.tmin
        green_times.append(g_time)
    return green_times

def check_phase_jump(traffic_light):
    traffic_light.pre_phase_index = traffic_light.cur_phase_index
    for i in range(len(traffic_light.inc_edges)):
        traffic_light.cur_phase_index += 1
        if traffic_light.cur_phase_index == len(traffic_light.inc_edges):
            traffic_light.cur_phase_index = 0
        if len(traffic_light.inrange_vehicles[traffic_light.cur_phase_index]) > 0:
            break

def set_green_phase(traffic_light):
    phase_edge = traffic_light.inc_edges[traffic_light.cur_phase_index]
    simulation.set_phase(traffic_light.id, traffic_light.green_phases[phase_edge])
    traffic_light.phase_status = 'g'
    traffic_light.phase_duration = traffic_light.cycle_green_times[traffic_light.cur_phase_index]

def set_yellow_phase(traffic_light):
    phase_edge = traffic_light.inc_edges[traffic_light.pre_phase_index]
    simulation.set_phase(traffic_light.id, traffic_light.yellow_phases[phase_edge])
    traffic_light.phase_status = 'y'
    traffic_light.phase_duration = 2

if __name__ == "__main__":
    websters_method()