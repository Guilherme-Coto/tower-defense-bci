# music_recall_bci

Classificador que decide **qual das faixas o participante está a recordar
mentalmente pelo ritmo**, a partir do dataset BIDS que enviaste
(`sub-01/ses-03`, paradigma `MusicMemoryRecall6Track`).

## O que descobri nos dados

O nome do "task" no filename BIDS diz `task-leftright` em todas as
sessões — é um artefacto de como o BIDS Recorder Suite nomeou os
ficheiros, **não** reflete o paradigma real. O paradigma verdadeiro está
no evento `Experiment_Start_..._Paradigm_...`:

- `ses-01`: motor imagery esquerda/direita (com e sem música de fundo)
- `ses-02`: paradigma "AllInOne4Class" (motor imagery 4 classes)
- `ses-03`: **`MusicMemoryRecall6Track`** — este é o que interessa aqui
- `ses-04`: gravação incompleta (falta `.vhdr`/eventos, não é usável)

Na `ses-03`, cada trial segue: `Cue_Audio_Sample_Track_N` (1s, ouve um
excerto) → `Task_Recall_Track_N` (~4-5s, recorda mentalmente o ritmo, sem
áudio) → `Rest`. São 30 trials, 6 faixas × 5 repetições, perfeitamente
balanceado. O `bids_loader.py` identifica sessões deste tipo pelo
conteúdo do `events.tsv`, não pelo nome do ficheiro — se gravares mais
sessões `MusicMemoryRecall`, basta correr o pipeline outra vez.

## Diferença importante face ao NMED-T

No NMED-T sabias a frequência de batida exata de cada música (ex.
FIRE=1.3736 Hz), por isso conseguias procurar potência nessa frequência
específica. Aqui **não há essa informação** (não sei o BPM das 6 faixas),
e as épocas são muito mais curtas (~4.5s vs. minutos no NMED-T — lembra
que no NMED-T o melhor resultado foi com janelas de ~50s). Por isso troquei
a abordagem:

- Em vez de potência em bins finos (0.1 Hz) numa frequência-alvo conhecida,
  uso **potência log em bandas clássicas** (delta/theta/alpha/beta) via
  multitaper, que é mais robusto com pouco sinal.
- Adicionei **parâmetros de Hjorth** (activity/mobility/complexity) por
  canal — captam modulação rítmica no domínio do tempo sem depender de
  conhecer a frequência exata.
- LDA com **shrinkage** (`solver='lsqr', shrinkage='auto'`) em vez de LDA
  normal — com 224 features e só 30 trials, a LDA normal sobreajusta.
- Validação por **Leave-One-Trial-Out** em vez de k-fold — com 5 trials
  por classe, é a opção com menos viés.

## Resultado (já correu, dados reais)

```
Acurácia global (LOO-CV): 33.3%  (chance = 16.7%, 30 trials, 6 classes)
```

~2× o nível de chance — na mesma ordem de grandeza do que já tinhas visto
no NMED-T (29-39% vs. 25% chance), o que é consistente dado que é o mesmo
tipo de sinal (entrainment rítmico) só que agora com muito menos dados
(30 trials de uma sessão vs. 20 sujeitos × 10 músicas).

Track_2 e Track_4 saem melhor (60%); Track_1 nunca é acertada (0/5) —
vale a pena veres se a Track_1 tem características rítmicas muito
parecidas com outra faixa, ou se há algum problema no trial (a Track_1
foi usada em 3 dos primeiros 4 trials, pode haver efeito de fadiga/
adaptação inicial).

## Estrutura

```
music_recall_bci/
├── config.py             # paths, bandas de frequência, janela de época
├── bids_loader.py        # localiza + carrega sessões de recall no BIDS
├── epoching.py           # extrai épocas alinhadas a Task_Recall_Track_N
├── features.py           # potência por banda (multitaper) + Hjorth
├── train_classifier.py   # LDA c/ shrinkage + validação Leave-One-Out
├── evaluate.py           # matriz de confusão, acurácia por classe
├── run_pipeline.py       # corre tudo de ponta a ponta
└── requirements.txt
```

## Como correr

```bash
pip install -r requirements.txt
python run_pipeline.py
```

Por defeito lê de `./datasets/datasets` (ajusta `BIDS_ROOT` em
`config.py` se necessário). O modelo final treinado em 100% dos dados
fica em `output/modelo_recall_musical.joblib`, pronto a carregar com
`joblib.load(...)` para inferência em tempo real.

## Próximos passos sugeridos

1. **Mais sessões/repetições.** 5 trials por classe é pouco para separar
   6 classes com confiança — o mesmo problema de generalização que já
   tens no NMED-T, mas agravado por N pequeno.
2. **Calibração por pessoa** (já é o teu plano para o Nautilus) — aqui
   nem se põe a questão de generalização entre sujeitos, é tudo o
   sub-01, o que ajuda a acurácia mas significa que este modelo não vai
   generalizar para outra pessoa.
3. Se conseguires o BPM real das 6 faixas, vale a pena voltar a testar a
   abordagem antiga (potência na frequência-alvo específica) e comparar
   com esta — pode ser que uma combinação das duas features dê melhor
   resultado.
