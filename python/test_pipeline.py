import random

from acquisition.simulator_receiver import SimulatorReceiver
from pipeline import BCIPipeline

receiver = SimulatorReceiver()
receiver.connect()

pipeline = BCIPipeline()

rhythms = ["FIRE", "WATER", "EARTH", "WIND"]

correct = 0
total = 100

for i in range(total):

    expected = random.choice(rhythms)

    receiver.set_rhythm(expected)

    prediction = None

    for _ in range(4):

        chunk = receiver.get_chunk()

        result = pipeline.process(chunk)

        if result is not None:
            prediction = result

    label, confidence = prediction

    if label == expected:
        correct += 1

    print(
        f"{i+1:03d} | "
        f"Expected={expected:6} "
        f"Predicted={label:6} "
        f"Conf={confidence:.3f}"
    )

print("\nAccuracy:", correct / total)