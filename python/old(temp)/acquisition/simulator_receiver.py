from acquisition.simulator import EEGSimulator

class SimulatorReceiver:

    def __init__(self, rhythm="FIRE"):
        self.simulator = EEGSimulator()
        self.rhythm = rhythm

    def connect(self):
        print("[Simulator] Connected")

    def get_chunk(self, duration=0.5):
        return self.simulator.generate(self.rhythm, duration=duration)

    def set_rhythm(self, rhythm):
        self.rhythm = rhythm