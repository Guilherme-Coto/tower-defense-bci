from pylsl import StreamInlet, resolve_stream

class LSLReceiver:

    def __init__(self):
        self.inlet = None

    def connect(self):
        print("Searching for LSL stream...")
        streams = resolve_stream('type', 'EEG')
        self.inlet = StreamInlet(streams[0])
        print("Connected!")

    def get_chunk(self):
        samples = []
        while len(samples) < 125:   # 0.5 s @250 Hz
            sample, timestamp = self.inlet.pull_sample()
            samples.append(sample)

        return samples