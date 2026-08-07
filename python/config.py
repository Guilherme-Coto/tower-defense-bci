# Configurações Gerais do Projeto BCI Tower Defense

IP = "127.0.0.1"
PORT = 5006

SAMPLING_RATE = 250
LOWCUT = 1.0
HIGHCUT = 40.0

# Configurações de Janelas para Data Augmentation & Real-time
WINDOW_SIZE_SEC = 2.0
WINDOW_STEP_SEC = 0.5  # Sobreposição de 75%

# Bandas de frequência (Hz)
BANDS = [
    (1, 4),    # Delta
    (4, 8),    # Theta
    (8, 13),   # Alpha
    (13, 30),  # Beta
    (30, 40),  # Gamma
]

TARGET_A = 3
TARGET_B = 5

# Elementos do Jogo
ELEMENTS = {
    0: "FIRE",
    1: "WATER",
    2: "WIND",
    3: "EARTH"
}

# Faixa alvo padrão para modelo binário (Track 1)
TARGET_TRACK = 6
MODE = "rhythm"
