# Tower Defense BCI

Integração entre o jogo **Tower Defense** (Godot 4) e um pipeline de **Brain-Computer Interface (BCI)** em Python para decodificação de ritmos mentais em tempo real.

O jogador controla o elemento da torre (Fogo, Água, Vento, Eletricidade) pensando no ritmo musical associado a cada fraqueza elemental. O sinal de EEG (g.Nautilus via LSL ou simulador BIDS) é processado continuamente e comanda a torre via UDP.

---

## Estrutura do Repositório

```text
tower-defense-bci/
├── tower_defense/      # Projeto Godot 4 (cenas, scripts, modelos 3D, áudio)
│   ├── scenes/         # Cenas do jogo (main_menu.tscn, scene_bci_gameplay.tscn, ...)
│   └── scripts/        # Lógica de jogo, spawner, UI e receptores UDP
├── python/             # Pipeline BCI em tempo real (aquisição, pré-processamento, FBCSP)
│   ├── main.py         # Executável principal com dashboard no terminal
│   ├── pipeline.py     # Coordenação do buffer rolante, predição e UDP
│   ├── config.py       # Portas, bandas de frequência e parâmetros globais
│   ├── models/         # Modelo de produção treinado (rhythm_model.joblib)
│   └── training/       # Script para treinar/atualizar o modelo
└── oz_server.py        # Servidor web local alternativo para testes manuais (Wizard of Oz)
```

---

## Pré-requisitos

1. **Godot 4.x** (testado em Godot 4.7 em Windows e Linux).
2. **Python >= 3.10** com [`uv`](https://github.com/astral-sh/uv) instalado (ou `pip`).

Instalação das dependências Python:
```bash
cd python
uv sync
```
*(As dependências incluem: `numpy`, `scipy`, `scikit-learn`, `pylsl`, `joblib`, `pandas`, `matplotlib`).*

---

## Como Executar

O sistema funciona com dois processos em paralelo: o **jogo (Godot)** e o **pipeline BCI (Python)**.

### 1. Iniciar o Jogo (Godot)

Abre o projeto no Godot Editor ou corre diretamente por terminal:
```bash
~/.local/bin/godot --path tower_defense
```

No menu principal, tens as seguintes opções:
- **Jogar (Modo BCI)**: Nova fase jogável interativa. A torre **não** escolhe poderes automaticamente; espera comandos do BCI (porta 4242) ou do teclado.
- **Treinar**: Cenas clássicas de calibração (*Recall* e *Imagine*) onde o jogo toca músicas e pisca o ecrã para recolha de dados BIDS.
- **Jogar (Modo Oz)**: Modo assistido para operação com `oz_server.py`.

---

### 2. Iniciar o Pipeline BCI (Python)

Abre outro terminal na pasta `python/` e escolhe o modo de entrada:

#### A. Com o amplificador g.Nautilus ao vivo (LSL)
Usa este modo durante as sessões de teste com a touca de EEG:
```bash
cd python
uv run python main.py --source lsl --auto-send --threshold 0.35
```

#### B. Com o Simulador BIDS (Replay de dados reais)
Reproduz a 250 Hz os ensaios reais gravados do sujeito (`sub-01/ses-01`):
```bash
cd python
uv run python main.py --source simulator --mode bids_replay --auto-send
```

#### C. Modo Interativo de Teste (Troca manual de ritmo no terminal)
Permite pressionar teclas (`1`, `2`, `3`, `4`) no terminal para alternar o sinal simulado e ver a torre mudar no jogo:
```bash
cd python
uv run python main.py --source simulator --interactive
```

---

## Como Funciona o Modo BCI

Na nova fase (`scene_bci_gameplay.tscn`), os inimigos avançam pelo caminho em direção à torre:

1. Quando um inimigo surge, o HUD no topo do ecrã indica:
   - O elemento do inimigo.
   - O ritmo mental que deves imaginar para o contrariar.
   - O estado atual da torre (`[EFICAZ! DANO 2X]` vs `[INEFICAZ]`).
2. A torre dispara automaticamente contra inimigos dentro do alcance, usando o elemento ativo.
3. Se o elemento contrariar a fraqueza do inimigo, causa **dano duplo (80 HP por tiro)** e elimina-o rapidamente. Se estiver no elemento errado, causa metade ou 0 de dano.
4. Se o inimigo alcançar a torre, consome um coração. O jogador perde se os 5 corações acabarem.

### Tabela de Fraquezas e Ritmos Mentais

| Inimigo a Caminho | Contra-Elemento Ideal | Música Associada | Banda EEG / Ritmo | Efeito |
| :--- | :--- | :--- | :--- | :--- |
| **Fogo** (0) | **Água** (1) | *Prelude in C Major* | Theta (4–8 Hz) | Dano 2x (80 HP) |
| **Água** (1) | **Eletricidade** (3) | *Waltz of the Flowers* | Gamma (30–45 Hz) | Dano 2x (80 HP) |
| **Vento** (2) | **Fogo** (0) | *Für Elise* | Alpha (8–12 Hz) | Dano 2x (80 HP) |
| **Eletricidade** (3) | **Vento** (2) | *The Four Seasons* | Beta (13–30 Hz) | Dano 2x (80 HP) |

> **Fallback Manual no Jogo**: Também podes carregar nos botões na interface ou usar as teclas `1` (Fogo), `2` (Água), `3` (Vento) e `4` (Eletricidade) diretamente no teclado.

---

## Comunicação e Portas de Rede (UDP)

A integração entre Godot e Python é feita via sockets UDP locais:

```text
 Python Pipeline                             Godot Tower Defense
┌─────────────────┐    UDP 4242 (Comandos)   ┌─────────────────────┐
│  UDPSender      │ ───────────────────────> │ BciReceiver         │
│                 │  power:0 .. power:3      │ (Autoload Singleton)│
│                 │                          │                     │
│ GameState       │    UDP 9000 (Marcadores) │ BCI_Marker_Send     │
│ Listener        │ <─────────────────────── │ (JSON de eventos)   │
└─────────────────┘                          └─────────────────────┘
```

- **Porta 4242 (Python -> Godot)**:
  - `power:0` a `power:3`: muda o elemento ativo da torre.
  - `kill_enemy`: elimina o inimigo ativo imediatamente.
  - `curar_jogador`: recupera um coração.
  - `spawn:0` a `spawn:3`: força o spawn de um elemento específico.
- **Porta 9000 (Godot -> Python)**:
  - Envia eventos do jogo em JSON: `{"name": "Trial_Start_Enemy_Fogo", "duration": 0.0}`.
  - Permite sincronizar a análise com fases de *Imagine*, *Rest* e *Enemy_Defeated*.

---

## Treino e Atualização do Modelo

O modelo de produção está guardado em `python/models/rhythm_model.joblib`.

Para retreinar com novos dados BIDS ou ajustar hiperparâmetros:
```bash
cd python
uv run python training/train_rhythm_decoder.py
```

O script treina um classificador **Filter-Bank CSP (FBCSP)** com 5 sub-bandas (Theta, Alpha, Low-Beta, High-Beta, Gamma) e Regressão Logística regularizada, utilizando os dados de audição e imaginação combinados.

Para correr a análise estatística completa (validações cruzadas, matrizes de confusão e RSA):
```bash
cd python
uv run python analysis/analyze_tower_defense_rhythm_decoding.py \
    --bids-root ../../nautilus_bci/scripts/bids/bids_tower_defense \
    --sub 01 \
    --ses 01 \
    --out-dir results/analysis
```

---

## Controlo Manual via Web (Wizard of Oz)

Se quiseres testar ou controlar o jogo a partir do telemóvel/browser sem correr o decodificador automático:
```bash
python oz_server.py
```
Acede a `http://localhost:5000` (ou pelo IP local da máquina na mesma rede Wi-Fi) para abrir a interface com botões táteis.

---

## Dicas e Resolução de Problemas

- **Porta UDP 4242 ocupada**: Verifica se não ficou nenhum processo anterior aberto com `ss -ulnp | grep 4242` ou `fuser -k 4242/udp`.
- **LSL não encontra a stream**: Certifica-te de que o g.NEEDaccess / conector g.Nautilus está a transmitir a stream LSL com o nome `g.Nautilus` (ou ajusta em `python/config.py`).
- **Ajustar sensibilidade do BCI**: Podes passar o argumento `--threshold 0.30` ou `--threshold 0.40` no `main.py` para alterar a confiança mínima necessária antes de enviar comandos para o jogo.
