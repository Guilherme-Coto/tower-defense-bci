from acquisition.simulator_receiver import SimulatorReceiver
from communication.udp_sender import UDPSender
from pipeline import BCIPipeline


def main():

    receiver = SimulatorReceiver("FIRE")
    receiver.connect()

    pipeline = BCIPipeline()

    udp = UDPSender()

    print("=== BCI Tower Defense ===")

    while True:

        rhythm = input("\nRitmo (FIRE/WATER/WIND/EARTH ou q): ").upper()

        if rhythm == "Q":
            break

        receiver.rhythm = rhythm

        prediction = None

        # 4 chunks de 0.5 s = 2 s
        for _ in range(4):
            chunk = receiver.get_chunk()
            result = pipeline.process(chunk)
            if result is not None:
                prediction = result

        if prediction is None:
            print("Sem previsão.")
            continue

        label, confidence = prediction

        print(f"\nEsperado   : {rhythm}")
        print(f"Previsto   : {label}")
        print(f"Confiança  : {confidence:.3f}")

        if confidence > 0.70:
            udp.send(label)
        else:
            print("Confiança demasiado baixa. Não enviado.")


if __name__ == "__main__":
    main()