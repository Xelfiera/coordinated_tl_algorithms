import traci

class TrafficLight:
    def __init__(self, tl_id):
        self.id = tl_id
        self.inc_edges = self.get_incoming_edges()
        self.out_edges = self.get_outgoing_edges()
        self.green_phases = self.get_green_phases()
        self.yellow_phases = self.get_yellow_phases()
        self.phase_status = 'g'
        self.phase_duration = 0
        self.pre_phase_index = 0
        self.phase_index = 0

    def get_incoming_edges(self):
        ctrl_lanes = traci.trafficlight.getControlledLanes(self.id)
        inc_edges = []
        for lane in ctrl_lanes:
            if lane[2] == '0' and lane[0:3] not in inc_edges:
                inc_edges.append(lane[0:3])
        return inc_edges

    def get_outgoing_edges(self):
        out_edges = []
        for edge in self.inc_edges:
            o_edge = edge.replace('0', '1', 2)
            out_edges.append(o_edge)
        return out_edges

    def get_green_phases(self):
        g_phases = []
        green_phases = {}
        logic = traci.trafficlight.getAllProgramLogics(self.id)[0]
        phases = logic.getPhases()
        for phase in phases:
            if 'G' in phase.state or 'g' in phase.state:
                g_phases.append(phase.state)
        for i in range(len(self.inc_edges)):
            green_phases[self.inc_edges[i]] = g_phases[i]
        return green_phases

    def get_yellow_phases(self):
        y_phases = []
        yellow_phases = {}
        logic = traci.trafficlight.getAllProgramLogics(self.id)[0]
        phases = logic.getPhases()
        for phase in phases:
            if 'y' in phase.state:
                y_phases.append(phase.state)
        for i in range(len(self.inc_edges)):
            yellow_phases[self.inc_edges[i]] = y_phases[i]
        return yellow_phases