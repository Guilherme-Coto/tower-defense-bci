import argparse
from pathlib import Path
import sys

import joblib
import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# Adicionar pasta raiz ao sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config


def train_and_evaluate(mode="binary", n_splits=5):
    data_dir = Path(__file__).resolve().parent

    X_path = data_dir / "X.npy"
    groups_path = data_dir / "groups.npy"

    if mode == "binary":
        y_path = data_dir / "y.npy"
        target_name = f"Binary (Track {config.TARGET_TRACK} vs Rest)"
    else:
        y_path = data_dir / "tracks.npy"
        target_name = "Multi-Class (6 Tracks)"

    if not X_path.exists() or not y_path.exists() or not groups_path.exists():
        print(f"Erro: Ficheiros de dados não encontrados em {data_dir}.")
        print("Por favor, execute primeiro: python training/build_dataset.py")
        return

    X = np.load(X_path)
    y = np.load(y_path)
    groups = np.load(groups_path)

    print("\n==========================================")
    print(f"TREINO BCI - MODO: {target_name}")
    print("==========================================")
    print(f"Shape X             : {X.shape}")
    print(f"Total de amostras   : {len(y)}")
    print(f"Grupos (Trials)     : {len(np.unique(groups))}")

    # Definir modelos a comparar com pesos de classe balanceados para evitar viés da classe maioritária
    classifiers = {
        "LDA (Shrinkage Auto)": LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto"),
        "SVM (RBF Kernel)": SVC(kernel="rbf", C=1.0, class_weight="balanced", random_state=42, probability=True),
        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=None,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            random_state=42
        )
    }

    # StratifiedGroupKFold garante que amostras da mesma classe e do mesmo trial não são divididas entre train e test
    sgkf = StratifiedGroupKFold(n_splits=n_splits)

    results = {}

    for name, clf in classifiers.items():
        print(f"\n---> A avaliar modelo: {name}")

        y_true_all = []
        y_pred_all = []
        fold_accs = []

        for fold, (train_idx, test_idx) in enumerate(sgkf.split(X, y, groups)):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Treino
            clf.fit(X_train_scaled, y_train)

            # Predição
            preds = clf.predict(X_test_scaled)

            acc = accuracy_score(y_test, preds)
            fold_accs.append(acc)

            y_true_all.extend(y_test)
            y_pred_all.extend(preds)

        mean_acc = np.mean(fold_accs)
        std_acc = np.std(fold_accs)
        macro_f1 = f1_score(y_true_all, y_pred_all, average="macro")

        results[name] = {
            "mean_acc": mean_acc,
            "std_acc": std_acc,
            "macro_f1": macro_f1,
            "clf_class": clf.__class__,
            "params": clf.get_params()
        }

        print(f"  Acurácia Média ({n_splits}-fold GroupKFold): {mean_acc:.3f} (+/- {std_acc:.3f})")
        print(f"  Macro F1-Score: {macro_f1:.3f}")
        print("\n  Matriz de Confusão Acumulada:")
        print(confusion_matrix(y_true_all, y_pred_all))

    # Selecionar o melhor modelo com base no Macro F1-Score (mais fiável com classes desbalanceadas)
    best_name = max(results, key=lambda k: results[k]["macro_f1"])
    print(f"\n==========================================")
    print(f"MELHOR MODELO (por Macro F1): {best_name}")
    print(f"Acurácia Global  : {results[best_name]['mean_acc']:.3f}")
    print(f"Macro F1-Score   : {results[best_name]['macro_f1']:.3f}")
    print("==========================================")


    # Treinar modelo final em 100% dos dados
    final_scaler = StandardScaler()
    X_scaled = final_scaler.fit_transform(X)

    best_clf = classifiers[best_name]
    best_clf.fit(X_scaled, y)

    # Guardar modelo e scaler
    models_dir = ROOT_DIR / "models"
    models_dir.mkdir(exist_ok=True)
    model_filepath = models_dir / "rhythm_model.joblib"

    artifact_to_save = {
        "scaler": final_scaler,
        "model": best_clf,
        "mode": mode,
        "model_name": best_name,
        "feature_count": X.shape[1]
    }

    joblib.dump(artifact_to_save, model_filepath)
    print(f"\nModelo final guardado com sucesso em: {model_filepath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Treino do modelo BCI Tower Defense.")
    parser.add_argument(
        "--mode",
        choices=["binary", "multiclass"],
        default="binary",
        help="Modo de treino: binary (Faixa Alvo vs Restantes) ou multiclass (6 faixas)"
    )
    parser.add_argument(
        "--splits",
        type=int,
        default=5,
        help="Número de splits para StratifiedGroupKFold"
    )

    args = parser.parse_args()
    train_and_evaluate(mode=args.mode, n_splits=args.splits)
