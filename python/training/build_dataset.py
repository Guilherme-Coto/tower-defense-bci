import re
from pathlib import Path

import mne
import numpy as np
import pandas as pd
import sys

# Adicionar pasta raiz ao inicio do sys.path para importar config e features globais
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config
from features.extractor import BCIFeatureExtractor

def build_dataset(
    dataset_dir="datasets",
    window_size_sec=config.WINDOW_SIZE_SEC,
    window_step_sec=config.WINDOW_STEP_SEC,
    target_track=config.TARGET_TRACK,
    lowcut=config.LOWCUT,
    highcut=config.HIGHCUT
):
    dataset_path = Path(dataset_dir)
    vhdr_files = sorted(dataset_path.rglob("*.vhdr"))
    print(f"\n==========================================")
    print(f"Encontrados {len(vhdr_files)} ficheiros EEG BIDS.")
    print(f"==========================================")

    extractor = BCIFeatureExtractor(fs=config.SAMPLING_RATE, bands=config.BANDS)

    X = []
    y_binary = []
    y_multiclass = []
    groups = []
    sessions = []

    global_trial_id = 0

    for vhdr in vhdr_files:
        print(f"\nA processar: {vhdr.relative_to(dataset_path.parent)}")
        session_name = vhdr.parent.parent.name

        try:
            raw = mne.io.read_raw_brainvision(
                vhdr,
                preload=True,
                verbose=False
            )
        except Exception as e:
            print(f"Erro ao ler {vhdr}: {e}")
            continue

        # Aplicar filtros
        raw.filter(lowcut, highcut, verbose=False)
        raw.notch_filter(50, verbose=False)

        fs = raw.info["sfreq"]

        events_file = vhdr.with_name(
            vhdr.name.replace("_eeg.vhdr", "_events.tsv")
        )

        if not events_file.exists():
            print("  [Aviso] events.tsv não encontrado.")
            continue

        events = pd.read_csv(events_file, sep="\t")
        recalls = events[
            events["trial_type"].str.contains("Task_Recall", na=False)
        ]

        print(f"  Eventos Task_Recall encontrados: {len(recalls)}")

        win_samples = int(window_size_sec * fs)
        step_samples = int(window_step_sec * fs)

        file_sample_count = 0

        for _, row in recalls.iterrows():
            trial_type = row["trial_type"]
            match = re.search(r"Track_(\d+)", trial_type)

            if match is None:
                continue

            track = int(match.group(1))
            start_sample = int(row["sample"])

            # duração normal
            if row["duration"] > 1:
                duration_samples = int(row["duration"] * fs)
                stop_sample = start_sample + duration_samples
            # duração = apenas marcador (0.1 s)
            else:
                next_events = events.iloc[row.name + 1:]
                rest_events = next_events[
                    next_events["trial_type"] == "Rest"
                ]

                if len(rest_events) == 0:
                    continue
 
                stop_sample = int(rest_events.iloc[0]["sample"])

            duration_samples = stop_sample - start_sample
            trial_eeg = raw.get_data(start=start_sample, stop=stop_sample)
    
            # Normalização por canal dentro do trial
            trial_eeg = trial_eeg - trial_eeg.mean(axis=1, keepdims=True)
            std = trial_eeg.std(axis=1, keepdims=True)
            std[std == 0] = 1e-8
            trial_eeg = trial_eeg / std

            # Extração de janelas sobrepostas (Data Augmentation)
            n_trial_samples = trial_eeg.shape[1]
            if n_trial_samples < win_samples:
                continue

            trial_window_count = 0

            for curr_start in range(0, n_trial_samples - win_samples + 1, step_samples):
                curr_stop = curr_start + win_samples
                window_data = trial_eeg[:, curr_start:curr_stop]

                feat = extractor.extract(window_data)

                X.append(feat)
                y_binary.append(1 if track == target_track else 0)
                y_multiclass.append(track)
                groups.append(global_trial_id)
                sessions.append(session_name)

                trial_window_count += 1
                file_sample_count += 1

            global_trial_id += 1

        print(f"  Janelas geradas neste ficheiro: {file_sample_count}")

    X = np.array(X, dtype=np.float32)
    y_binary = np.array(y_binary, dtype=np.int32)
    y_multiclass = np.array(y_multiclass, dtype=np.int32)
    groups = np.array(groups, dtype=np.int32)
    sessions = np.array(sessions)

    print("\n==========================================")
    print("DATASET CRIADO COM SUCESSO")
    print("==========================================")
    print(f"Shape X             : {X.shape}")
    print(f"Total de Janelas    : {len(y_binary)}")
    print(f"Total de Trials (Grupos): {len(np.unique(groups))}")

    print("\nDistribuição Binária (Track 1 vs Rest):")
    unique_b, counts_b = np.unique(y_binary, return_counts=True)
    for u, c in zip(unique_b, counts_b):
        lbl = f"Track {target_track}" if u == 1 else "Outras Track"
        print(f"  Classe {u} ({lbl}): {c} janelas")

    print("\nDistribuição Multi-Classe (1 a 6):")
    unique_m, counts_m = np.unique(y_multiclass, return_counts=True)
    for u, c in zip(unique_m, counts_m):
        print(f"  Track {u}: {c} janelas")

    output_dir = Path(__file__).resolve().parent
    np.save(output_dir / "X.npy", X)
    np.save(output_dir / "y.npy", y_binary)
    np.save(output_dir / "tracks.npy", y_multiclass)
    np.save(output_dir / "groups.npy", groups)
    np.save(output_dir / "sessions.npy", sessions)

    print(f"\nFicheiros guardados em: {output_dir}")
    return X, y_binary, y_multiclass, groups

if __name__ == "__main__":
    build_dataset()
