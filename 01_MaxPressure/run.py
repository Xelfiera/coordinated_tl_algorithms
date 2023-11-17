import traci
from Utils import simulation
from Utils.trafficlight import TrafficLight
import math

def max_pressure():
    simulation.start()
    traffic_lights = create_tls(traci.trafficlight.getIDList())  # Create TrafficLight object each per traffic light in simulation.

    while traci.simulation.getMinExpectedNumber() > 0:
        for tl_id in traffic_lights.keys():
            if traffic_lights[tl_id].phase_duration == 0:
                if traffic_lights[tl_id].phase_status == 'g':
                    traffic_lights[tl_id].pre_phase_index = traffic_lights[tl_id].cur_phase_index
                    traffic_lights[tl_id].cur_phase_index = calc_max_pressure(traffic_lights[tl_id])

                    if traffic_lights[tl_id].pre_phase_index != traffic_lights[tl_id].cur_phase_index:
                        set_yellow_phase(traffic_lights[tl_id])
                    else:
                        traffic_lights[tl_id].phase_duration = simulation.tmin

                elif traffic_lights[tl_id].phase_status == 'y':
                    set_green_phase(traffic_lights[tl_id])

            traffic_lights[tl_id].phase_duration -= 1
        traci.simulationStep()

def create_tls(tl_ids):
    traffic_lights = {}
    for tl_id in tl_ids:
        traffic_lights[tl_id] = TrafficLight(tl_id)
    return traffic_lights

def calc_max_pressure(traffic_light):
    tl_position = traci.junction.getPosition(traffic_light.id)
    inc_veh_counts = get_inrange_vehicles(tl_position, traffic_light.inc_edges)
    out_veh_counts = get_inrange_vehicles(tl_position, traffic_light.out_edges)

    pressures = []
    for i in range(len(traffic_light.inc_edges)):
        pressures.append(inc_veh_counts[i] - out_veh_counts[i])

    mx_pressure_index = 0
    mx_pressure = pressures[0]
    for i, pressure in enumerate(pressures):
        if pressure > mx_pressure:
            mx_pressure_index = i
            mx_pressure = pressure
    return mx_pressure_index

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
        vehicles_in_range.append(len(edge_vehicles))
    return vehicles_in_range

def set_green_phase(traffic_light):
    phase_edge = traffic_light.inc_edges[traffic_light.cur_phase_index]
    simulation.set_phase(traffic_light.id, traffic_light.green_phases[phase_edge])
    traffic_light.phase_status = 'g'
    traffic_light.phase_duration = simulation.tmin

def set_yellow_phase(traffic_light):
    phase_edge = traffic_light.inc_edges[traffic_light.pre_phase_index]
    simulation.set_phase(traffic_light.id, traffic_light.yellow_phases[phase_edge])
    traffic_light.phase_status = 'y'
    traffic_light.phase_duration = 2

if __name__ == "__main__":
    max_pressure()