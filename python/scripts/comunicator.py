import socket
import time
import numpy as np

#classe responsável por detetar os beats
from beat_detector import Beat_Detector

#configurações da rede
GODOT_IP = "127.0.0.1"
GODOT_PORT = 5006
THRESHOLD = 0.40  

#esta função vai ser para ir buscar os dados reais do nautilus, 
#ao meu do futuro pedir o script que le dados do nautilus para
#integrar na função estilo adapter(ads finalmente deu jeito)
def capture_eeg_data(hz_alvo=None, detector=None):
    # --- ZONA DE SIMULAÇÃO (Substituir isto pelo Nautilus mais tarde) ---
    # Gera uma onda com a frequência do elemento escolhido + ruído
    if hz_alvo is not None and detector is not None:
        onda_pura = np.sin(2 * np.pi * hz_alvo * detector.t + 0.7)
        ruido = np.random.normal(0, 3.0, len(detector.t))
        return onda_pura + ruido
    # ------------------------------------------------------------------

    return None

def main():
    #inicia a classe e o socket
    detector = Beat_Detector()
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
            hz_alvo = detector.music_specs[elemento_alvo]["hz"]
            
            # Executa a captura através do Adapter
            sinal_eeg = capture_eeg_data(hz_alvo, detector)
            
            #processa o sinal
            scores = detector.calculate_similarity(sinal_eeg)
            
            print("\nScores de Encaixe:")
            for k, v in scores.items():
                print(f"  -> {k}: {v:.4f}")
                
            vencedor = max(scores, key=scores.get)
            score_vencedor = scores[vencedor]
            
            print(f"\n[BCI] Vencedor: {vencedor} ({score_vencedor:.4f})")
            
            #só envia para o godot se passar o threshold
            if score_vencedor >= THRESHOLD:
                mensagem = f"TRIGGER_{vencedor}"
                sock.sendto(mensagem.encode('utf-8'), (GODOT_IP, GODOT_PORT))
                print(f"👉 [UDP] Pacote enviado: '{mensagem}'")
            else:
                print("❌ [UDP] Sinal fraco. Ignorado.")
                
            print("\n")
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nA terminar...")
    finally:
        sock.close()
        print("Ponte UDP fechada com sucesso.")

if __name__ == "__main__":
    main()