import numpy as np
import scipy.signal as signal


class Beat_Detector:
    def __init__(self, sampling_rate=125, window_duration=15.0):
        self.fs = sampling_rate
        self.duration = window_duration
        self.t = np.linspace(0, self.duration, int(self.fs * self.duration), endpoint=False)

        # configuração atual: músicas mais altas e mais espaçadas entre si,
        # para reduzir tanto a confusão espectral (frequências próximas)
        # como o desequilíbrio de ruído 1/f (frequências muito baixas)
        self.music_specs = {
            "EARTH": {"bpm": 74.26,  "hz": 1.2376},  # Song 3 - Tiptoes
            "FIRE":  {"bpm": 91.46,  "hz": 1.5244},  # Song 5 - Lebanese Blonde
            "WATER": {"bpm": 108.70, "hz": 1.8116},  # Song 7 - Doing Yoga
            "WIND":  {"bpm": 128.21, "hz": 2.1368},  # Song 9 - Silent Shout
        }

        # parâmetros da deteção espectral (FFT + SNR local)
        self.guarda_hz = 0.15         # zona excluída à volta de cada frequência-alvo
        self.banda_ruido_min = 0.5    # banda larga e comum, partilhada por todas
        self.banda_ruido_max = 4.0    # as frequências, para nunca ficar sem bins

    def preprocess_signal(self, raw_eeg_window):
        """Filtro passa-banda para limpar ruídos (mantém apenas entre 0.5 Hz e 10 Hz)"""
        nyquist = 0.5 * self.fs
        low = 0.5 / nyquist
        high = 10.0 / nyquist
        b, a = signal.butter(4, [low, high], btype='band')
        return signal.filtfilt(b, a, raw_eeg_window)

    def calculate_similarity(self, eeg_window):
        """Deteta a frequência dominante via SNR espectral (FFT), comparando
        a potência em cada frequência-alvo com a potência da sua própria
        vizinhança imediata. Isto neutraliza o ruído 1/f porque cada
        frequência só é julgada contra o "chão" local dela, e não contra
        as outras frequências diretamente."""

        limpo = self.preprocess_signal(eeg_window)
        limpo = (limpo - np.mean(limpo)) / (np.std(limpo) + 1e-8)

        # janela de Hanning para reduzir vazamento espectral entre bins vizinhos
        janela_hanning = np.hanning(len(limpo))
        sinal_janelado = limpo * janela_hanning

        fft_vals = np.fft.rfft(sinal_janelado)
        potencia = np.abs(fft_vals) ** 2
        freqs = np.fft.rfftfreq(len(sinal_janelado), d=1.0 / self.fs)

        # zona de exclusão GLOBAL: guarda à volta de TODAS as frequências
        # conhecidas, para o pico genuíno de uma música nunca ser contado
        # como "ruído de fundo" ao avaliar outra música vizinha
        todas_as_freqs = [info["hz"] for info in self.music_specs.values()]
        exclusao_global = np.zeros_like(freqs, dtype=bool)
        for f in todas_as_freqs:
            exclusao_global |= (np.abs(freqs - f) <= self.guarda_hz)

        # máscara de ruído ÚNICA e larga, partilhada por todas as frequências
        # -- evita ficar sem bins disponíveis quando as zonas de guarda dos
        # vizinhos comem quase toda uma janela estreita por-frequência
        mascara_ruido = (
            (freqs >= self.banda_ruido_min) &
            (freqs <= self.banda_ruido_max) &
            (~exclusao_global)
        )
        if np.any(mascara_ruido):
            piso_ruido_global = np.median(potencia[mascara_ruido]) + 1e-8
        else:
            piso_ruido_global = np.median(potencia) + 1e-8

        raw_scores = {}
        for name, info in self.music_specs.items():
            freq_alvo = info["hz"]

            idx_alvo = np.argmin(np.abs(freqs - freq_alvo))
            potencia_alvo = potencia[idx_alvo]

            raw_scores[name] = potencia_alvo / piso_ruido_global

        soma_scores = sum(raw_scores.values()) + 1e-8
        scores = {name: mag / soma_scores for name, mag in raw_scores.items()}
        return scores