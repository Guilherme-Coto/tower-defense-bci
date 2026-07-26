import numpy as np
import scipy.io as sio
from beat_detector import Beat_Detector

FICHEIROS = {
    "FIRE":  ("data_imputed/song25_Imputed.mat", 25),
    "WATER": ("data_imputed/song27_Imputed.mat", 27),
    "WIND":  ("data_imputed/song29_Imputed.mat", 29),
    "EARTH": ("data_imputed/song30_Imputed.mat", 30),
}

CANAL = 117  # <-- põe aqui o canal que escolheste

detector = Beat_Detector(sampling_rate=125, window_duration=15.0)
tamanho_janela = int(15.0 * 125)

for alvo, (caminho, trigger) in FICHEIROS.items():
    mat_data = sio.loadmat(caminho)
    dados = mat_data[f"data{trigger}"]  # [canais, tempo, sujeitos]
    n_sujeitos = dados.shape[2]

    vitorias_por_elemento = {"FIRE": 0, "WATER": 0, "WIND": 0, "EARTH": 0}

    for sujeito in range(n_sujeitos):
        sinal = dados[CANAL, :tamanho_janela, sujeito]
        scores = detector.calculate_similarity(sinal)
        vencedor = max(scores, key=scores.get)
        vitorias_por_elemento[vencedor] += 1

    print(f"Alvo real: {alvo} -> distribuição entre os {n_sujeitos} sujeitos: {vitorias_por_elemento}")