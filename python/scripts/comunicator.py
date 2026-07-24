import socket, time
import numpy as np
import scipy.io as sio
import pickle, os

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

BASELINE_CACHE_PATH = "baseline_global.pkl"

#def calibrar_baseline_global(detector):
#    if os.path.exists(BASELINE_CACHE_PATH):
#        with open(BASELINE_CACHE_PATH, "rb") as f:
#            baseline = pickle.load(f)
#        print("Baseline global carregada da cache.")
#        detector.baseline = baseline
#        return
#
#    ficheiros = {
#        "1": "data_imputed/song21_Imputed.mat",
#        "2": "data_imputed/song25_Imputed.mat",
#        "3": "data_imputed/song28_Imputed.mat",
#        "4": "data_imputed/song30_Imputed.mat"
#    }
#
#    print("A calcular baseline global (só precisa de correr uma vez)...")
#    sinais = []
#    for escolha, caminho in ficheiros.items():
#        sinal, _ = _ler_mat_stanford(caminho, escolha)
#        sinais.append(sinal)
#
#    sinal_combinado = np.concatenate(sinais)
#    detector.calibrate_baseline(sinal_combinado)
#
#    with open(BASELINE_CACHE_PATH, "wb") as f:
#        pickle.dump(detector.baseline, f)
#    print("Baseline global calculada e guardada em cache.")

#esta função vai ser para ir buscar os dados reais do nautilus, 
#ao meu do futuro pedir o script que le dados do nautilus para
#integrar na função estilo adapter(ads finalmente deu jeito)
def capture_eeg_data(hz_alvo=None, detector=None):
    global CURSOR_ATUAL, DATASET_ATUAL, FS_DATASET
    
    if DATASET_ATUAL is None:
        return None

    tamanho_janela = int(15.0 * FS_DATASET) #15 segundos
    avanco = int(1 * FS_DATASET) # Anda 1 seg para a frente

    # Verifica se ainda temos dados para ler (Dimensão 1 é o tempo)
    if CURSOR_ATUAL + tamanho_janela < DATASET_ATUAL.shape[1]:
        # Corta: [Canal 0, Tempo, Sujeito 0]
        sinal_eeg = DATASET_ATUAL[62, CURSOR_ATUAL : CURSOR_ATUAL + tamanho_janela, 0]
        
        CURSOR_ATUAL += avanco
        return sinal_eeg
    else:
        print("Fim do dataset!")
        return None

    #desativado para testar com os datasets
    # --- ZONA DE SIMULAÇÃO ---
    # Gera uma onda com a frequência do elemento escolhido + ruído
    #if hz_alvo is not None and detector is not None:
    #    onda_pura = np.sin(2 * np.pi * hz_alvo * detector.t + 0.7)
    #    ruido = np.random.normal(0, 3.0, len(detector.t))
    #    return onda_pura + ruido
    # ------------------------------------------------------------------
    #
    #return None

def carregar_dataset_stanford(escolha):
    global DATASET_ATUAL, CURSOR_ATUAL, FS_DATASET
    
    ficheiros = {
        "1": "data_imputed/song21_Imputed.mat",
        "2": "data_imputed/song25_Imputed.mat",
        "3": "data_imputed/song28_Imputed.mat",
        "4": "data_imputed/song30_Imputed.mat",
    }
    
    caminho = ficheiros.get(escolha)
    if not caminho:
        return False
    
    print(f"A carregar ficheiro {caminho}...")
    mat_data = sio.loadmat(caminho)
    
    CURSOR_ATUAL = 0
    FS_DATASET = int(mat_data['fs'][0][0])
    
    trigger = TRIGGER_POR_ESCOLHA[escolha]
    chave_data = f"data{trigger}"
    DATASET_ATUAL = mat_data[chave_data]
    print(f"Dataset carregado com sucesso! FS = {FS_DATASET}Hz")
    return True

TRIGGER_POR_ESCOLHA = {
    "1": 21,
    "2": 25,
    "3": 28,
    "4": 30,
}

def _ler_mat_stanford(caminho, escolha):
    mat_data = sio.loadmat(caminho)
    fs = int(mat_data['fs'][0][0])
    
    trigger = TRIGGER_POR_ESCOLHA[escolha]
    chave_data = f"data{trigger}"
    sinal = mat_data[chave_data][62, :, 0]
    return sinal, fs

def main():
    #inicia a classe e o socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("-- Ponte para o Godot iniciada --")
    print(f"A enviar comandos para o Godot em {GODOT_IP}:{GODOT_PORT}\n")
    
    #detector_base = Beat_Detector(sampling_rate=125, window_duration=15.0)
    #baseline_global = detector_base.baseline

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

            detector = Beat_Detector(sampling_rate=FS_DATASET, window_duration=15.0)
            #detector.baseline = baseline_global   # reaproveita a baseline global
            hz_alvo = detector.music_specs[elemento_alvo]["hz"]

            #inicia a classe com o FS lido do ficheiro
            detector = Beat_Detector(sampling_rate=FS_DATASET, window_duration=15.0)
            
            #calibração
            #sinal_completo = DATASET_ATUAL[62, :, 0]
            #detector.calibrate_baseline(sinal_completo)

            hz_alvo = detector.music_specs[elemento_alvo]["hz"]
            
            print("Inicio da leitura do dataset...")
            try:
                elements_count = {
                    "FIRE" : 0,
                    "WATER" : 0,
                    "WIND" : 0,
                    "EARTH" : 0
                }

                #loop até ao fim do dataset
                while True:
                    sinal_eeg = capture_eeg_data(hz_alvo, detector)
                    
                    if sinal_eeg is None:
                        print("Fim da leitura do dataset...")
                        break #fim da música
                        
                    scores = detector.calculate_similarity(sinal_eeg)
                       
                    vencedor = max(scores, key=scores.get)
                    score_vencedor = scores[vencedor]
                    
                    if score_vencedor >= THRESHOLD:
                        elements_count[vencedor]+=1
                        print("SCORE ATUAL: ")
                        print("FIRE:",elements_count["FIRE"])
                        print("WATER",elements_count["WATER"])
                        print("WIND:",elements_count["WIND"])
                        print("EARTH:",elements_count["EARTH"])
                        print()

                        mensagem = f"TRIGGER_{vencedor}"
                        sock.sendto(mensagem.encode('utf-8'), (GODOT_IP, GODOT_PORT))
                        print(f"[UDP] Pacote enviado: '{mensagem}' | Score: {score_vencedor:.4f}")
                    else:
                        print(f"[UDP] Vencedor {vencedor} mas sinal fraco ({score_vencedor:.4f}).")
                        
                    time.sleep(0.5)
            except KeyboardInterrupt:
                print("\nLeitura do dataset interrompida.")


            # Executa a captura através do Adapter
            #sinal_eeg = capture_eeg_data(hz_alvo, detector)
            
            #processa o sinal
            #scores = detector.calculate_similarity(sinal_eeg)
            
            #print("\nScores de Encaixe:")
            #for k, v in scores.items():
                #print(f"  -> {k}: {v:.4f}")
                
            #vencedor = max(scores, key=scores.get)
            #score_vencedor = scores[vencedor]
            
            #print(f"\n[BCI] Vencedor: {vencedor} ({score_vencedor:.4f})")
            
            #só envia para o godot se passar o threshold
            #if score_vencedor >= THRESHOLD:
                #mensagem = f"TRIGGER_{vencedor}"
                #sock.sendto(mensagem.encode('utf-8'), (GODOT_IP, GODOT_PORT))
                #print(f"[UDP] Pacote enviado: '{mensagem}'")
            #else:
                #print("[UDP] Sinal fraco. Ignorado.")
                
            #print("\n")
            #time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nA terminar...")
    finally:
        sock.close()
        print("Ponte UDP fechada com sucesso.")

if __name__ == "__main__":
    main()