"""
Script de calibração offline: encontra o(s) melhor(es) canal(is) EEG
para detetar as 4 frequências-alvo, usando SNR espectral via FFT.

Corre isto UMA VEZ, fora do main.py, para descobrir qual canal usar.
Depois só copias o número do canal escolhido para o DATASET_ATUAL[X, ...]
no teu código principal.
"""

import numpy as np
import scipy.io as sio

# --- Ajusta estes 4 caminhos e frequências às músicas escolhidas ---
MUSICAS = {
    "EARTH": {"ficheiro": "data_imputed/song23_Imputed.mat", "trigger": 23, "hz": 1.2376},
    "FIRE":  {"ficheiro": "data_imputed/song25_Imputed.mat", "trigger": 25, "hz": 1.5244},
    "WATER": {"ficheiro": "data_imputed/song27_Imputed.mat", "trigger": 27, "hz": 1.8116},
    "WIND":  {"ficheiro": "data_imputed/song29_Imputed.mat", "trigger": 29, "hz": 2.1368},
}

N_CANAIS = 124  # elétrodos 1-124 são válidos, segundo o paper (excluindo os da face)
GUARDA_HZ = 0.15   # zona excluída à volta do pico ao medir ruído
JANELA_RUIDO_HZ = 0.5  # até onde olhar para medir o ruído local


def snr_espectral(sinal, fs, freq_alvo):
    """Calcula o SNR espectral de um sinal numa frequência-alvo específica."""
    sinal = sinal - np.mean(sinal)
    janela_hanning = np.hanning(len(sinal))
    sinal_janelado = sinal * janela_hanning

    fft_vals = np.fft.rfft(sinal_janelado)
    potencia = np.abs(fft_vals) ** 2
    freqs = np.fft.rfftfreq(len(sinal_janelado), d=1.0 / fs)

    idx_alvo = np.argmin(np.abs(freqs - freq_alvo))
    potencia_alvo = potencia[idx_alvo]

    mascara_ruido = (
        (np.abs(freqs - freq_alvo) > GUARDA_HZ) &
        (np.abs(freqs - freq_alvo) <= JANELA_RUIDO_HZ)
    )
    piso_ruido = np.median(potencia[mascara_ruido]) + 1e-8

    return potencia_alvo / piso_ruido


def main():
    # snr_matriz[nome_ficheiro][nome_freq_testada] = array de SNR por canal
    # -- testamos as 4 frequências em CADA ficheiro, não só a frequência "certa"
    # desse ficheiro. Isto permite medir especificidade: um canal só é bom se a
    # resposta a uma frequência for MUITO mais forte no ficheiro certo do que
    # nos outros 3 (o que distingue resposta real de artefacto sempre presente).
    snr_matriz = {}

    for nome_ficheiro, info in MUSICAS.items():
        print(f"A processar ficheiro de {nome_ficheiro} ({info['ficheiro']})...")
        mat_data = sio.loadmat(info["ficheiro"])
        fs = int(mat_data["fs"][0][0])
        chave_data = f"data{info['trigger']}"
        dados = mat_data[chave_data]  # [canais, tempo, sujeitos]

        # média entre os 20 sujeitos -> aumenta o SNR real,
        # porque a resposta ao estímulo é fase-consistente entre pessoas
        media_sujeitos = np.mean(dados, axis=2)  # [canais, tempo]

        snr_matriz[nome_ficheiro] = {}
        for nome_freq, info_freq in MUSICAS.items():
            snrs = np.zeros(N_CANAIS)
            for canal in range(N_CANAIS):
                snrs[canal] = snr_espectral(media_sujeitos[canal, :], fs, info_freq["hz"])
            snr_matriz[nome_ficheiro][nome_freq] = snrs

    # índice de especificidade por canal e por frequência:
    # SNR no ficheiro certo, a dividir pela média do SNR dessa MESMA frequência
    # nos outros 3 ficheiros (onde não devia haver resposta real a essa frequência)
    especificidade = {}
    for nome_freq in MUSICAS:
        snr_proprio = snr_matriz[nome_freq][nome_freq]  # ficheiro certo, freq certa
        outros = [nome for nome in MUSICAS if nome != nome_freq]
        snr_outros = np.mean([snr_matriz[outro][nome_freq] for outro in outros], axis=0)
        especificidade[nome_freq] = snr_proprio / (snr_outros + 1e-8)

    # combina a especificidade das 4 frequências por canal (média geométrica,
    # para exigir que o canal seja específico nas 4, não só numa)
    matriz_especificidade = np.vstack([especificidade[nome] for nome in MUSICAS])
    score_combinado = np.exp(np.mean(np.log(matriz_especificidade + 1e-8), axis=0))

    ranking = np.argsort(score_combinado)[::-1]

    print("\n=== TOP 10 CANAIS por ESPECIFICIDADE (0-indexed) ===")
    print(f"{'Canal':>6} {'Score':>10} " + " ".join(f"{n:>8}" for n in MUSICAS))
    for canal in ranking[:10]:
        linha = " ".join(f"{especificidade[n][canal]:8.2f}" for n in MUSICAS)
        print(f"{canal:6d} {score_combinado[canal]:10.3f} {linha}")

    print("\n(valores de especificidade > 1 significam que a resposta é mais forte")
    print("no ficheiro certo do que nos outros 3 -- é isso que queremos ver)")

    melhor_canal = ranking[0]
    print(f"\n>>> Melhor canal: {melhor_canal} <<<")
    print("Usa este número em DATASET_ATUAL[melhor_canal, ...] no teu main.py")


if __name__ == "__main__":
    main()