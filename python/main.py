"""
main.py
=======
Real-Time BCI Tower Defense Rhythm Decoding Studio & Game Bridge.

Decodes 4 mental rhythms in real-time with the Godot Tower Defense game:
  - FIRE        (Element 0 / Track Für Elise)
  - WATER       (Element 1 / Track Prelude in C Major)
  - WIND        (Element 2 / Track The Four Seasons)
  - ELECTRICITY (Element 3 / Track Waltz of the Flowers)

Usage:
  # Run in simulator mode (replaying real BIDS sub-01 trials at 250 Hz):
  uv run python main.py --source simulator --mode bids_replay --auto-send

  # Run with live g.Nautilus EEG over LSL:
  uv run python main.py --source lsl --auto-send --threshold 0.35

  # Run in interactive simulator mode:
  uv run python main.py --source simulator --interactive
"""

import os
import sys
import time
import argparse
import select
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config
from pipeline import BCIPipeline
from acquisition.lsl_receiver import LSLReceiver
from acquisition.simulator_receiver import SimulatorReceiver


def print_banner(source_type, mode, auto_send, threshold):
    print("\n" + "=" * 84)
    print(" BCI TOWER DEFENSE: REAL-TIME 4-CLASS RHYTHM DECODING PIPELINE ".center(84, "="))
    print("=" * 84)
    print(f" • Input Source     : {source_type.upper()} ({mode if source_type == 'simulator' else '250 Hz LSL'})")
    print(f" • Godot Bridge     : UDP -> {config.GODOT_IP}:{config.GODOT_PORT} (power:0..3)")
    print(f" • Marker Listener  : UDP <- {config.GODOT_IP}:{config.GAME_MARKER_PORT} (game state)")
    print(f" • Model            : FilterBank CSP + Logistic Regression ({config.MODEL_PATH.name})")
    print(f" • Auto-Send Godot  : {'ENABLED' if auto_send else 'DISABLED'}")
    print(f" • Active Threshold : {threshold * 100:.1f}% (Chance baseline: 25.0%)")
    print("=" * 84 + "\n")


def format_bar(val, max_val=1.0, width=20):
    val_clamped = max(0.0, min(max_val, val))
    filled = int(round((val_clamped / max_val) * width))
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {val_clamped * 100:5.1f}%"


def check_stdin_nonblocking():
    """Checks if a character was pressed on stdin without blocking (Linux)."""
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline().strip().upper()
        return line
    return None


def run_pipeline(
    source="simulator",
    mode="bids_replay",
    auto_send=True,
    threshold=config.CONFIDENCE_THRESHOLD,
    interactive=False,
    duration_step=config.WINDOW_STEP_SEC
):
    print_banner(source, mode, auto_send, threshold)

    # 1. Initialize Pipeline
    pipeline = BCIPipeline(
        model_path=config.MODEL_PATH,
        confidence_threshold=threshold,
        auto_send_godot=auto_send,
        sync_game_markers=True
    )

    # 2. Initialize EEG Receiver
    if source.lower() == "lsl":
        receiver = LSLReceiver(
            stream_name=config.LSL_STREAM_NAME,
            stream_type=config.LSL_STREAM_TYPE,
            expected_channels=config.N_CHANNELS
        )
    else:
        receiver = SimulatorReceiver(initial_rhythm="FIRE", mode=mode)

    try:
        receiver.connect()
    except Exception as e:
        print(f"[Error] Failed to connect receiver: {e}")
        pipeline.close()
        return

    print("[*] Pipeline started. Streaming EEG chunks...")
    if source == "simulator" and interactive:
        print("    [Interactive Controls] Press '1': FIRE, '2': WATER, '3': WIND, '4': ELECTRICITY, 'Q': Quit + Enter\n")
    else:
        print("    Press Ctrl+C to terminate.\n")

    start_time = time.time()
    frames_count = 0

    try:
        while True:
            # Handle interactive user inputs in simulator mode
            if interactive and source == "simulator":
                user_cmd = check_stdin_nonblocking()
                if user_cmd:
                    if user_cmd == "Q":
                        print("[*] Quitting by user command.")
                        break
                    elif user_cmd in ["1", "F", "FIRE"]:
                        receiver.set_rhythm("FIRE")
                        print("\n>>> Simulated Mental Rhythm Switched to: [FIRE]\n")
                    elif user_cmd in ["2", "W", "WATER"]:
                        receiver.set_rhythm("WATER")
                        print("\n>>> Simulated Mental Rhythm Switched to: [WATER]\n")
                    elif user_cmd in ["3", "N", "WIND"]:
                        receiver.set_rhythm("WIND")
                        print("\n>>> Simulated Mental Rhythm Switched to: [WIND]\n")
                    elif user_cmd in ["4", "E", "ELECTRICITY"]:
                        receiver.set_rhythm("ELECTRICITY")
                        print("\n>>> Simulated Mental Rhythm Switched to: [ELECTRICITY]\n")

            # Fetch EEG chunk
            chunk = receiver.get_chunk(duration=duration_step)
            if chunk is None or len(chunk) == 0:
                time.sleep(0.02)
                continue

            # In simulator mode, pace generation to real-time (250 Hz)
            if source == "simulator":
                time.sleep(duration_step * 0.95)

            # Process through pipeline
            result = pipeline.process_chunk(chunk)
            frames_count += 1

            if result is not None:
                elem = result['element']
                conf = result['confidence']
                probs = result['probabilities']
                active = result['is_rhythm_active']
                game_st = result.get('game_state', 'N/A')
                sent = result.get('command_sent', False)

                bar_str = format_bar(conf, 1.0, 16)
                p_f = probs.get('FIRE', 0.0) * 100
                p_w = probs.get('WATER', 0.0) * 100
                p_wi = probs.get('WIND', 0.0) * 100
                p_e = probs.get('ELECTRICITY', 0.0) * 100

                status_tag = f"\033[92m[ACTIVE]\033[0m" if active else f"\033[90m[REST]\033[0m"
                elem_color = {
                    'FIRE': '\033[91m',
                    'WATER': '\033[94m',
                    'WIND': '\033[92m',
                    'ELECTRICITY': '\033[93m'
                }.get(elem, '\033[0m')
                elem_str = f"{elem_color}{elem:<11}\033[0m"

                action_str = f"-> Godot power:{result['element_id']}" if sent else ""

                print(
                    f"\r[{game_st:^7}] {status_tag} Decoded: {elem_str} {bar_str} | "
                    f"F:{p_f:4.1f}% W:{p_w:4.1f}% WI:{p_wi:4.1f}% E:{p_e:4.1f}% {action_str}",
                    end="",
                    flush=True
                )

    except KeyboardInterrupt:
        print("\n\n[*] Interrupted by user (Ctrl+C). Shutting down...")
    finally:
        total_time = max(0.1, time.time() - start_time)
        fps = pipeline.total_windows_processed / total_time
        print("\n" + "-" * 84)
        print(f" Summary: {pipeline.total_windows_processed} rhythm windows decoded in {total_time:.1f}s ({fps:.1f} windows/sec)")
        print("-" * 84)
        receiver.close()
        pipeline.close()


def main():
    parser = argparse.ArgumentParser(description="Real-Time BCI Tower Defense Rhythm Decoding Studio")
    parser.add_argument("--source", type=str, default="simulator", choices=["simulator", "lsl"],
                        help="EEG source: 'simulator' (BIDS replay/synthetic) or 'lsl' (live g.Nautilus)")
    parser.add_argument("--mode", type=str, default="bids_replay", choices=["bids_replay", "synthetic"],
                        help="Simulator mode: 'bids_replay' (real BIDS trials) or 'synthetic'")
    parser.add_argument("--threshold", type=float, default=config.CONFIDENCE_THRESHOLD,
                        help=f"Confidence threshold to trigger rhythm (default: {config.CONFIDENCE_THRESHOLD})")
    parser.add_argument("--auto-send", action="store_true", default=True,
                        help="Automatically trigger Godot element power when confidence > threshold")
    parser.add_argument("--no-auto-send", dest="auto_send", action="store_false",
                        help="Disable automatic triggering of Godot powers")
    parser.add_argument("--interactive", action="store_true", default=False,
                        help="Enable interactive keyboard rhythm switching in simulator mode")

    args = parser.parse_args()
    run_pipeline(
        source=args.source,
        mode=args.mode,
        auto_send=args.auto_send,
        threshold=args.threshold,
        interactive=args.interactive
    )


if __name__ == "__main__":
    main()