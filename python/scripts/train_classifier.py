"""
Módulo de treino LDA para EEG.
"""

import sys
import pickle
import numpy as np
import scipy.io as sio
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, accuracy_score
from pathlib import Path

from features import extrair_features


class Tee:
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()

    def flush(self):
        for f in self.files:
            f.flush()


MUSICAS = {
    "EARTH": {"ficheiro": "data_imputed/song23_Imputed.mat", "trigger": 23, "hz": 1.2376},
    "FIRE":  {"ficheiro": "data_imputed/song24_Imputed.mat", "trigger": 24, "hz": 1.3736},
    "WATER": {"ficheiro": "data_imputed/song26_Imputed.mat", "trigger": 26, "hz": 1.6026},
    "WIND":  {"ficheiro": "data_imputed/song29_Imputed.mat", "trigger": 29, "hz": 2.1368},
}

CANAIS_USADOS = [35, 95, 107, 69, 100, 116, 99, 106, 29, 103,
                 117, 66, 36, 56, 57, 17, 58, 28, 19, 111]

AVANCO_SEGUNDOS = 5.0  
JANELA_SEGUNDOS = 50.0
MODELO_PATH = "model.pkl"


def construir_dataset(janela_segundos=JANELA_SEGUNDOS, avanco_segundos=AVANCO_SEGUNDOS):
    nomes_elementos = list(MUSICAS.keys())
    freqs_alvo = [MUSICAS[nome]["hz"] for nome in nomes_elementos]

    X, y, groups = [], [], []

    for nome_elemento, info in MUSICAS.items():
        print(f"A extrair features de {nome_elemento} ({info['ficheiro']})...")
        mat_data = sio.loadmat(info["ficheiro"])
        fs = int(mat_data["fs"][0][0])
        dados = mat_data[f"data{info['trigger']}"]

        tamanho_janela = int(janela_segundos * fs)
        avanco = int(avanco_segundos * fs)
        n_sujeitos = dados.shape[2]
        n_tempo = dados.shape[1]

        for sujeito in range(n_sujeitos):
            inicio = 0
            while inicio + tamanho_janela < n_tempo:
                janela = dados[:, inicio:inicio + tamanho_janela, sujeito]
                feats = extrair_features(janela, fs, freqs_alvo, CANAIS_USADOS)

                X.append(feats)
                y.append(nome_elemento)
                groups.append(sujeito)
                inicio += avanco

        del mat_data, dados

    return np.array(X), np.array(y), np.array(groups), nomes_elementos, freqs_alvo


def validar_leave_one_subject_out(X, y, groups, nomes_elementos):
    print("\n=== Validação leave-one-subject-out ===")
    logo = LeaveOneGroupOut()
    y_real_todos, y_pred_todos = [], []

    for treino_idx, teste_idx in logo.split(X, y, groups):
        scaler = StandardScaler()
        X_treino = scaler.fit_transform(X[treino_idx])
        X_teste = scaler.transform(X[teste_idx])

        clf = LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")
        clf.fit(X_treino, y[treino_idx])

        y_pred = clf.predict(X_teste)
        y_real_todos.extend(y[teste_idx])
        y_pred_todos.extend(y_pred)

    acc = accuracy_score(y_real_todos, y_pred_todos)
    print(f"\nTaxa de acerto global (leave-one-subject-out): {acc*100:.1f}%")
    print(f"(acaso puro com {len(nomes_elementos)} classes seria {100/len(nomes_elementos):.1f}%)")

    cm = confusion_matrix(y_real_todos, y_pred_todos, labels=nomes_elementos)
    print("\nMatriz de confusão (linhas = real, colunas = previsto):")
    print(f"{'':>8}" + "".join(f"{n:>8}" for n in nomes_elementos))
    for i, nome in enumerate(nomes_elementos):
        print(f"{nome:>8}" + "".join(f"{cm[i][j]:>8}" for j in range(len(nomes_elementos))))

    return acc, cm


def treinar_modelo_final(X, y, nomes_elementos, freqs_alvo, janela_segundos):
    print("\nA treinar o modelo final com todos os sujeitos...")
    scaler = StandardScaler()
    X_norm = scaler.fit_transform(X)

    clf = LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")
    clf.fit(X_norm, y)

    modelo = {
        "clf": clf,
        "scaler": scaler,
        "canais_usados": CANAIS_USADOS,
        "nomes_elementos": nomes_elementos,
        "freqs_alvo": freqs_alvo,
        "janela_segundos": janela_segundos,
    }

    with open(MODELO_PATH, "wb") as f:
        pickle.dump(modelo, f)
    print(f"Modelo guardado em {MODELO_PATH}")


# Função principal que o script de automação vai chamar
def executar_treino(janela_segundos=JANELA_SEGUNDOS, avanco_segundos=AVANCO_SEGUNDOS):
    pasta_destino = Path("results") / "train_classifier"
    pasta_destino.mkdir(parents=True, exist_ok=True)

    contador = 1
    while True:
        caminho_arquivo = pasta_destino / f"train_classifier_{contador}.txt"
        if not caminho_arquivo.exists():
            break
        contador += 1

    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        stdout_original = sys.stdout
        sys.stdout = Tee(sys.stdout, f)

        try:
            print(f">>> A TESTAR COM: Janela = {janela_segundos}s | Avanço = {avanco_segundos}s")
            X, y, groups, nomes_elementos, freqs_alvo = construir_dataset(janela_segundos, avanco_segundos)
            print(f"\nDataset construído: {X.shape[0]} amostras, {X.shape[1]} features cada.")

            acc, cm = validar_leave_one_subject_out(X, y, groups, nomes_elementos)
            treinar_modelo_final(X, y, nomes_elementos, freqs_alvo, janela_segundos)

        finally:
            sys.stdout = stdout_original

    print(f"\n[OK] Ficheiro de log guardado em: {caminho_arquivo}")
    return acc


if __name__ == "__main__":
    executar_treino()