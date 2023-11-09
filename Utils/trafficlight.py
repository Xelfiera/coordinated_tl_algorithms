import traci

class TrafficLight:
    def __init__(self, tl_id):
        self.id = tl_id
        self.ctrl_edges = self.get_controlled_edges()
        self.green_phases = self.get_green_phases()
        self.yellow_phases = self.get_yellow_phases()
        self.phase_duration = 0

    def get_controlled_edges(self):
        ctrl_lanes = traci.trafficlight.getControlledLanes(self.id)
        ctrl_edges = []
        for lane in ctrl_lanes:
            if lane[2] == '0' and lane[0:3] not in ctrl_edges:
                ctrl_edges.append(lane[0:3])
        return ctrl_edges

    def get_green_phases(self):
        g_phases = []
        green_phases = {}
        logic = traci.trafficlight.getAllProgramLogics(self.id)[0]
        phases = logic.getPhases()
        for phase in phases:
            if 'G' in phase.state or 'g' in phase.state:
                g_phases.append(phase.state)
        for i in range(len(self.ctrl_edges)):
            green_phases[self.ctrl_edges[i]] = g_phases[i]
        return green_phases

    def get_yellow_phases(self):
        y_phases = []
        yellow_phases = {}
        logic = traci.trafficlight.getAllProgramLogics(self.id)[0]
        phases = logic.getPhases()
        for phase in phases:
            if 'y' in phase.state:
                y_phases.append(phase.state)
        for i in range(len(self.ctrl_edges)):
            yellow_phases[self.ctrl_edges[i]] = y_phases[i]
        return yellow_phases