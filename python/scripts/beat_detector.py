import numpy as np
import scipy.signal as signal

class Beat_Detector:
    def __init__(self, sampling_rate=250, window_duration=3.0):
        self.fs = sampling_rate  #amostras por segundo
        self.duration = window_duration  #análise de 3 segundos
        self.t = np.linspace(0, self.duration, int(self.fs * self.duration), endpoint=False)
        
        #cada elemento está associado a uns Hz e bpm
        self.music_specs = {
            "FIRE":  {"hz": 1.95, "bpm": 117}, # Billie Jean
            "WATER":  {"hz": 1.00, "bpm": 60},  # Zen Ambient
            "WIND":    {"hz": 2.67, "bpm": 160},  # Electro Trance
            "EARTH": {"hz": 2.33, "bpm": 140}, # Heavy March
        }
        
        # Gerar os templates matemáticos (Seno e Cosseno)
        self.templates = {}
        for name, info in self.music_specs.items():
            freq = info["hz"]
            sine_wave = np.sin(2 * np.pi * freq * self.t)
            cosine_wave = np.cos(2 * np.pi * freq * self.t)
            self.templates[name] = (sine_wave, cosine_wave)
    
    def preprocess_signal(self, raw_eeg_window):
        """Filtro passa-banda para limpar ruídos (mantém apenas entre 0.5 Hz e 10 Hz)"""
        nyquist = 0.5 * self.fs
        low = 0.5 / nyquist
        high = 10.0 / nyquist
        b, a = signal.butter(4, [low, high], btype='band')
        return signal.filtfilt(b, a, raw_eeg_window)

    def calculate_similarity(self, eeg_window):
        """Compara o sinal com os 4 templates e devolve os scores"""
        limpo = self.preprocess_signal(eeg_window)
        
        # Normalização estatística do sinal
        limpo = (limpo - np.mean(limpo)) / (np.std(limpo) + 1e-8)
        
        scores = {}
        for name, (sine_temp, cosine_temp) in self.templates.items():
            # Correlação linear com ambas as fases
            r_sine = np.corrcoef(limpo, sine_temp)[0, 1]
            r_cosine = np.corrcoef(limpo, cosine_temp)[0, 1]
            
            # Magnitude combinada (Teorema de Pitágoras)
            scores[name] = np.sqrt(r_sine**2 + r_cosine**2)
            
        return scores