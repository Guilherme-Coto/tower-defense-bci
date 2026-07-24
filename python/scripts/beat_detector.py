import numpy as np
import scipy.signal as signal

class Beat_Detector:
    def __init__(self, sampling_rate=250, window_duration=6.0):
        self.fs = sampling_rate  #amostras por segundo
        self.duration = window_duration  #análise de 3 segundos
        self.t = np.linspace(0, self.duration, int(self.fs * self.duration), endpoint=False)
        
        #(está desativo para eu testar com datasets)
        #cada elemento está associado a uns Hz e bpm
        #self.music_specs = {
        #    "FIRE":  {"hz": 1.95, "bpm": 117}, # Billie Jean
        #    "WATER":  {"hz": 1.00, "bpm": 60},  # Zen Ambient
        #    "WIND":    {"hz": 2.67, "bpm": 160},  # Electro Trance
        #    "EARTH": {"hz": 2.33, "bpm": 140}, # Heavy March
        #}

        #configuração para os datasets de stanford
        self.music_specs = {
            "FIRE":  {"bpm": 55.97,  "hz": 0.9328}, #21
            "WATER": {"bpm": 91.46,  "hz": 1.5244}, #25
            "WIND":  {"bpm": 120.00, "hz": 2.0000}, #28
            "EARTH": {"bpm": 150.00, "hz": 2.5000} #30
        }

        # Gerar os templates matemáticos (Seno e Cosseno)
        #self.templates = {}
        #for name, info in self.music_specs.items():
        #    freq = info["hz"]
        #    sine_wave = np.sin(2 * np.pi * freq * self.t)
        #    cosine_wave = np.cos(2 * np.pi * freq * self.t)
        #    self.templates[name] = (sine_wave, cosine_wave)

        # frequências "nulas" para medir o ruído de fundo em CADA janela,
        # afastadas o suficiente (>=0.25Hz) de qualquer frequência real
        hz_reais = [info["hz"] for info in self.music_specs.values()]
        candidatos = np.arange(0.5, 2.8, 0.05)
        self.null_freqs = [
            f for f in candidatos
            if all(abs(f - hz) >= 0.2 for hz in hz_reais)
        ]
        #self.null_templates = []
        #for f in self.null_freqs:
        #    s = np.sin(2 * np.pi * f * self.t)
        #    c = np.cos(2 * np.pi * f * self.t)
        #    self.null_templates.append((s, c))
   
    def calibrate_baseline(self, full_signal, step=None):
        """Corre uma janela deslizante sobre full_signal e mede a magnitude 
        média de correlação 'ao acaso' para cada frequência. Chama isto uma 
        vez antes de usar calculate_similarity com correção."""
        if step is None:
            step = int(1 * self.fs)
        win_len = int(self.duration * self.fs)
        
        sums = {name: 0.0 for name in self.music_specs}
        count = 0
        
        for start in range(0, len(full_signal) - win_len, step):
            janela = full_signal[start:start + win_len]
            limpo = self.preprocess_signal(janela)
            limpo = (limpo - np.mean(limpo)) / (np.std(limpo) + 1e-8)
            
            for name, (sine_temp, cosine_temp) in self.templates.items():
                r_sine = np.corrcoef(limpo, sine_temp)[0, 1]
                r_cosine = np.corrcoef(limpo, cosine_temp)[0, 1]
                mag = np.sqrt(r_sine**2 + r_cosine**2)
                sums[name] += mag
            count += 1
        
        self.baseline = {name: (sums[name] / count) + 1e-8 for name in self.music_specs}
        print("Baseline calibrado:", self.baseline)

    def preprocess_signal(self, raw_eeg_window):
        """Filtro passa-banda para limpar ruídos (mantém apenas entre 0.5 Hz e 10 Hz)"""
        nyquist = 0.5 * self.fs
        low = 0.5 / nyquist
        high = 10.0 / nyquist
        b, a = signal.butter(4, [low, high], btype='band')
        return signal.filtfilt(b, a, raw_eeg_window)
    
    def calculate_similarity(self, eeg_window):
        """Deteta a frequência dominante via SNR espectral (FFT), 
        em vez de correlação com templates. Robusto ao ruído 1/f porque 
        compara cada frequência-alvo só com a sua vizinhança imediata."""
        
        limpo = self.preprocess_signal(eeg_window)
        limpo = (limpo - np.mean(limpo)) / (np.std(limpo) + 1e-8)
        
        # janela de Hanning para reduzir vazamento espectral (spectral leakage)
        janela_hanning = np.hanning(len(limpo))
        sinal_janelado = limpo * janela_hanning
        
        # FFT e espectro de potência
        fft_vals = np.fft.rfft(sinal_janelado)
        potencia = np.abs(fft_vals) ** 2
        freqs = np.fft.rfftfreq(len(sinal_janelado), d=1.0 / self.fs)
        
        resolucao = freqs[1] - freqs[0]  # resolução espectral desta janela
        
        raw_scores = {}
        for name, info in self.music_specs.items():
            freq_alvo = info["hz"]
            
            # potência no(s) bin(s) mais próximo(s) da frequência-alvo
            idx_alvo = np.argmin(np.abs(freqs - freq_alvo))
            potencia_alvo = potencia[idx_alvo]
            
            # vizinhança para medir o ruído local: exclui uma "zona de guarda"
            # perto do alvo (para não incluir o próprio pico) e olha um pouco 
            # mais longe para cima e para baixo
            guarda = 0.15  # Hz — zona excluída à volta do alvo
            janela_ruido = 0.5  # Hz — até onde olhar para medir o ruído local
            
            mascara_ruido = (
                (np.abs(freqs - freq_alvo) > guarda) &
                (np.abs(freqs - freq_alvo) <= janela_ruido)
            )
            
            if np.any(mascara_ruido):
                piso_ruido_local = np.median(potencia[mascara_ruido]) + 1e-8
            else:
                piso_ruido_local = np.median(potencia) + 1e-8
            
            raw_scores[name] = potencia_alvo / piso_ruido_local
        
        soma_scores = sum(raw_scores.values()) + 1e-8
        scores = {name: mag / soma_scores for name, mag in raw_scores.items()}
        return scores