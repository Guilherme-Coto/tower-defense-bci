import socket, time
import numpy as np
import scipy.io as sio

#classe responsável por detetar os beats
from beat_detector import Beat_Detector

#configurações da rede
GODOT_IP = "127.0.0.1"
GODOT_PORT = 5006
THRESHOLD = 0.33

#variáveis globais para ler o dataset
DATASET_ATUAL = None
CURSOR_ATUAL = 0
FS_DATASET = 125

#canal EEG escolhido via find_best_channel.py — troca este valor pelo
#resultado desse script (o "Melhor canal" impresso no fim)
MELHOR_CANAL = 116  # <-- placeholder, substituir pelo resultado real

#músicas escolhidas (mais altas e mais espaçadas em Hz) e o trigger
#correspondente no ficheiro .mat de cada uma (ver NMED-T_README.pdf)
FICHEIROS_DATASET = {
    "1": "data_imputed/song25_Imputed.mat",  # FIRE  - Lebanese Blonde, 1.5244 Hz
    "2": "data_imputed/song27_Imputed.mat",  # WATER - Doing Yoga, 1.8116 Hz
    "3": "data_imputed/song29_Imputed.mat",  # WIND  - Silent Shout, 2.1368 Hz
    "4": "data_imputed/song23_Imputed.mat",  # EARTH - Tiptoes, 1.2376 Hz
}

TRIGGER_POR_ESCOLHA = {
    "1": 25,
    "2": 27,
    "3": 29,
    "4": 23,
}


def capture_eeg_data():
    global CURSOR_ATUAL, DATASET_ATUAL, FS_DATASET

    if DATASET_ATUAL is None:
        return None

    tamanho_janela = int(15.0 * FS_DATASET)  # 15 segundos
    avanco = int(1 * FS_DATASET)  # Anda 1 seg para a frente

    # Verifica se ainda temos dados para ler (Dimensão 1 é o tempo)
    if CURSOR_ATUAL + tamanho_janela < DATASET_ATUAL.shape[1]:
        # Corta: [Canal escolhido, Tempo, Sujeito 0]
        sinal_eeg = DATASET_ATUAL[MELHOR_CANAL, CURSOR_ATUAL: CURSOR_ATUAL + tamanho_janela, 0]

        CURSOR_ATUAL += avanco
        return sinal_eeg
    else:
        print("Fim do dataset!")
        return None


def carregar_dataset_stanford(escolha):
    global DATASET_ATUAL, CURSOR_ATUAL, FS_DATASET

    caminho = FICHEIROS_DATASET.get(escolha)
    if not caminho:
        return False

    print(f"A carregar ficheiro {caminho}...")
    mat_data = sio.loadmat(caminho)

    # reset o cursor
    CURSOR_ATUAL = 0

    # Lê a frequência de amostragem guardada no ficheiro (geralmente 125)
    FS_DATASET = int(mat_data['fs'][0][0])

    # Guarda a matriz gigante [canais, amostras, sujeitos]
    trigger = TRIGGER_POR_ESCOLHA[escolha]
    chave_data = f"data{trigger}"
    DATASET_ATUAL = mat_data[chave_data]
    print(f"Dataset carregado com sucesso! FS = {FS_DATASET}Hz")
    return True


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("-- Ponte para o Godot iniciada --")
    print(f"A enviar comandos para o Godot em {GODOT_IP}:{GODOT_PORT}\n")

    try:
        while True:
            #interface simples para escolher a pessoa
            print("--------------------------------------------------")
            print("Escolha o elemento para simular o sinal cerebral:")
            print("1 - FIRE | 2 - WATER | 3 - WIND | 4 - EARTH | 0 - Sair")

            escolha = input("Opção: ").strip()

            if escolha == "0":
                break

            mapeamento = {"1": "FIRE", "2": "WATER", "3": "WIND", "4": "EARTH"}
            if escolha not in mapeamento:
                print("Opção inválida. Tenta novamente.")
                continue

            elemento_alvo = mapeamento[escolha]

            if not carregar_dataset_stanford(escolha):
                print("Erro ao carregar o ficheiro. Verifica se a pasta 'data_imputed' está no sítio certo.")
                continue

            #inicia a classe com o FS lido do ficheiro
            detector = Beat_Detector(sampling_rate=FS_DATASET, window_duration=15.0)
            hz_alvo = detector.music_specs[elemento_alvo]["hz"]

            print("Inicio da leitura do dataset...")
            try:
                elements_count = {
                    "FIRE": 0,
                    "WATER": 0,
                    "WIND": 0,
                    "EARTH": 0
                }

                #loop até ao fim do dataset
                while True:
                    sinal_eeg = capture_eeg_data()

                    if sinal_eeg is None:
                        print("Fim da leitura do dataset...")
                        break  #fim da música

                    scores = detector.calculate_similarity(sinal_eeg)
                    print("DEBUG scores:", {k: round(v, 4) for k, v in scores.items()})

                    vencedor = max(scores, key=scores.get)
                    score_vencedor = scores[vencedor]

                    if score_vencedor >= THRESHOLD:
                        elements_count[vencedor] += 1
                        print("SCORE ATUAL: ")
                        print("FIRE:", elements_count["FIRE"])
                        print("WATER", elements_count["WATER"])
                        print("WIND:", elements_count["WIND"])
                        print("EARTH:", elements_count["EARTH"])
                        print()

                        mensagem = f"TRIGGER_{vencedor}"
                        sock.sendto(mensagem.encode('utf-8'), (GODOT_IP, GODOT_PORT))
                        print(f"[UDP] Pacote enviado: '{mensagem}' | Score: {score_vencedor:.4f}")
                    else:
                        print(f"[UDP] Vencedor {vencedor} mas sinal fraco ({score_vencedor:.4f}).")

                    time.sleep(0.5)
            except KeyboardInterrupt:
                print("\nLeitura do dataset interrompida.")

    except KeyboardInterrupt:
        print("\nA terminar...")
    finally:
        sock.close()
        print("Ponte UDP fechada com sucesso.")


if __name__ == "__main__":
    main()