# BCI Tower Defense: Pipeline de Decodificação de Ritmos em Tempo Real

Pipeline BCI de tempo real integrado com o jogo Godot **Tower Defense**, utilizando os algoritmos de decodificação neural baseados no script `analyze_tower_defense_rhythm_decoding.py`.

O sistema decodifica em tempo real em qual dos 4 ritmos / elementos o jogador está a pensar (imaginação motora/rítmica ou perceção auditiva) e ativa automaticamente os poderes correspondentes na torre do jogo:

| ID | Elemento | Faixa Musical Associada | Banda Dominante | Ação no Jogo (UDP 4242) |
|---|---|---|---|---|
| **0** | **FIRE** | *Für Elise* | Alpha (8–12 Hz) | `power:0` |
| **1** | **WATER** | *Prelude in C Major* | Theta (4–8 Hz) | `power:1` |
| **2** | **WIND** | *The Four Seasons* | Low/High-Beta (13–30 Hz) | `power:2` |
| **3** | **ELECTRICITY** | *Waltz of the Flowers* | Gamma (30–45 Hz) | `power:3` |

---

## 🧠 Arquitetura do Pipeline

```
[g.Nautilus EEG via LSL] ou [Simulador BIDS Replay (250 Hz)]
                        │
                        ▼
   [SlidingWindow Ring Buffer] (3.0s = 750 amostras, passo 0.25s)
                        │
                        ▼
         [EEGPreprocessor] (Tempo Real)
           ├── Filtro Passa-Banda Butterworth (1.0 - 45.0 Hz, 4ª ordem)
           ├── Filtro Notch IIR (50.0 Hz)
           └── Referenciação Espacial Robust CAR (Median CAR)
                        │
                        ▼
     [FilterBankCSPClassifier (FBCSP)]
           ├── 5 Bandas: Theta, Alpha, Low-Beta, High-Beta, Gamma
           ├── Filtros Espaciais CSP One-vs-Rest (OVR) por banda
           ├── Projeção de variância logarítmica (80 features)
           └── Classificador Regularizado (Regressão Logística / LDA)
                        │
                        ▼
         [Predição de Probabilidades & Confiança]
           ├── Elemento Previsto: FIRE / WATER / WIND / ELECTRICITY
           ├── Distribuição de Probabilidades [P_0, P_1, P_2, P_3]
           └── Deteção de Estado: Ativo (confiança >= threshold) vs. Rest
                        │
                        ▼
        [Integração Bidirecional com Godot]
           ├── UDP 4242: Envio automático do comando `power:{id}`
           └── UDP 9000: Escuta de marcadores de fase (`Imagine`, `Listen`, `Rest`)
```

---

## 🚀 Como Executar

### 1. Modo Simulador com Replay BIDS (Recomendado para Testes)
Replay em tempo real (250 Hz) das épocas reais gravadas no dataset BIDS (`sub-01/ses-01`):

```bash
cd tower-defense-bci/python
uv run python main.py --source simulator --mode bids_replay --auto-send
```

### 2. Modo Simulador Interativo (Troca Manual de Ritmo)
Permite pressionar teclas (`1`: Fogo, `2`: Água, `3`: Vento, `4`: Elétrica) no terminal para simular transições de ritmo:

```bash
uv run python main.py --source simulator --interactive
```

### 3. Modo Tempo Real com o Headset g.Nautilus (LSL)
Conecta-se diretamente ao fluxo LSL de 32 canais a 250 Hz:

```bash
uv run python main.py --source lsl --auto-send --threshold 0.35
```

---

## 🛠️ Re-treino e Análise do Modelo

Para re-treinar o modelo de produção exportado para `models/rhythm_model.joblib`:

```bash
uv run python training/train_rhythm_decoder.py
```

Para executar o estúdio completo de neuro-estatística (validação cruzada LOSO, matrizes de confusão, RSA e gráficos de publicação):

```bash
uv run python analysis/analyze_tower_defense_rhythm_decoding.py \
    --bids-root /home/guilhermecoto/Documentos/Lasige/nautilus_bci/scripts/bids/bids_tower_defense \
    --sub 01 \
    --ses 01 \
    --out-dir results/analysis
```

---

## 📊 Desempenho Obtido nos Dados Reais

No dataset BIDS Tower Defense (`sub-01/ses-01`):
- **Transferência Zero-Shot (Treino em Audição -> Teste em Imaginação)**: **51.32%** de acurácia (chance = 25.0%).
- **Validação Cruzada 5-Fold Estratificada (Listen + Imagine combinados)**: **40.15% ± 4.98%**.
- **Acurácia de Ajuste (Self-Fit de Produção)**: **69.08%**.
- **Alinhamento RSA (Spearman $\rho$ entre Audição e Imaginação)**: $\rho = 0.600$, confirmando a partilha de representações neurais córtico-auditivas e motoras durante a imaginação do ritmo.

---

## 📁 Estrutura de Ficheiros em `tower-defense-bci/python`

```
python/
├── config.py                           # Parâmetros globais, portas UDP, bandas de frequência
├── pipeline.py                         # BCIPipeline: coordena aquisição, filtro, decodificação e rede
├── main.py                             # Executável de tempo real com dashboard no terminal
│
├── acquisition/
│   ├── lsl_receiver.py                 # Receptor LSL para o g.Nautilus
│   ├── simulator.py                    # Gerador sintético e reprodutor de dados brutos BIDS
│   └── simulator_receiver.py           # Interface unificada para o simulador
│
├── preprocessing/
│   ├── preprocessor.py                 # Filtro passa-banda (1-45 Hz), notch (50 Hz) e Robust CAR
│   ├── spatial_filters.py              # Robust CAR, detetor de canais ruidosos e Laplacian
│   └── window.py                       # SlidingWindow FIFO de 3.0 segundos
│
├── classifier/
│   ├── rhythm_decoder.py               # FilterBankCSPClassifier e RhythmPredictor
│   └── predictor.py                    # Alias retrocompatível
│
├── communication/
│   ├── udp_sender.py                   # Envia comandos de poder (power:0..3) para o Godot (UDP 4242)
│   ├── game_state_listener.py          # Escuta marcadores de fase do jogo Godot (UDP 9000)
│   └── udp_to_lsl_bridge.py            # Ponte UDP -> LSL para gravação BIDS
│
├── models/
│   ├── rhythm_model.joblib             # Modelo treinado pronto a usar em tempo real
│   └── rhythm_decoding_report.json     # Métricas detalhadas de treino e matriz de confusão
│
├── training/
│   └── train_rhythm_decoder.py         # Script de treino automatizado
│
└── analysis/
    ├── analyze_tower_defense_rhythm_decoding.py # Script de análise neuro-estatística BIDS
    └── spatial_filters.py              # Filtros espaciais
```
