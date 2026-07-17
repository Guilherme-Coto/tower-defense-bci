import socket
import numpy as np
from pylsl import StreamInfo, StreamOutlet
import time
import json
import msvcrt 

#configuração das portas
UDP_IP = "127.0.0.1"
RECEIVE_PORT = 5005
SEND_PORT = 5006

#socket para ouvir do godot
sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_in.bind((UDP_IP, RECEIVE_PORT))
sock_in.setblocking(False) 

#socket para comunicar com o godot
sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#cria o simulador eeg
info_eeg = StreamInfo('VirtualEEG', 'EEG', 8, 250, 'float32', 'bci_lasige_2026')
outlet_eeg = StreamOutlet(info_eeg)

# Memória do Dataset
dados_eeg_guardados = []
timestamps_eeg = []
eventos_jogo = []
taxa_amostragem = 250.0

#foco atual
foco_atual = "FIRE_MARKER"

print("[ESTADO DO SERVIDOR]")
print(f"Servidor Ativo")
print(f"Está à escuta na porta {RECEIVE_PORT} | Envia respostas pela porta {SEND_PORT}")
print(f"Estado de foco: {foco_atual}")
print("[Estados: 1=Fogo | 2=Água | 3=Vento | 4=Terra]\n")

try:
    while True:
        #faz a simulação do eeg
        amostra_eeg = np.random.normal(0, 20, 8).tolist()
        ts_atual = time.time()
        outlet_eeg.push_sample(amostra_eeg, ts_atual)
        dados_eeg_guardados.append(amostra_eeg)
        timestamps_eeg.append(ts_atual)
        
        #troca o foco atual
        if msvcrt.kbhit():
            tecla = msvcrt.getch().decode('utf-8')
            if tecla == '1':
                foco_atual = "FIRE_MARKER"
                print(f"\nAlterou o foco para Fogo.")
            elif tecla == '2':
                foco_atual = "WATER_MARKER"
                print(f"\nAlterou o foco para Àgua")
            elif tecla == '3':
                foco_atual = "WIND_MARKER"
                print(f"\nAlterou o foco para Vento")
            elif tecla == '4':
                foco_atual = "EARTH_MARKER"
                print(f"\nAlterou o foco para Terra")

        try:
            #recebe os dados do godot
            data, addr = sock_in.recvfrom(1024)
            marcador = data.decode('utf-8')
            ts_jogo = time.time()
            
            eventos_jogo.append({"evento": marcador, "timestamp": ts_jogo})
            
            #verifica se o marcador a piscar é igual ao foco
            if marcador == foco_atual:
                #aqui assume-se que foi perfeito
                timing_p300 = np.random.uniform(290, 350)
                print(f"Foco correto: {marcador}! Tempo: ({timing_p300:.1f}ms)")

                #envia para o godot o foco
                sock_out.sendto(foco_atual.encode('utf-8'), (UDP_IP, SEND_PORT))
            else:
                print(f"Marcador recebido: {marcador}. Ignorar(Focado em {foco_atual})")
                
        except BlockingIOError:
            pass
                
        time.sleep(1.0 / taxa_amostragem)

except KeyboardInterrupt:
    print("\nA guardar dataset final...")
    dataset = {"eeg_data": dados_eeg_guardados, "eeg_timestamps": timestamps_eeg, "events": eventos_jogo}
    with open("meu_dataset_teste.json", "w") as f:
        json.dump(dataset, f)
    print("Ficheiro guardado!")