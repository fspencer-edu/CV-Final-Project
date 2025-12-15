import subprocess
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

scripts = [
    os.path.join(SCRIPT_DIR, "cali_cam.py"),
    os.path.join(SCRIPT_DIR, "clean.py"),
    os.path.join(SCRIPT_DIR, "preprocess.py"),
    os.path.join(SCRIPT_DIR, "gen_cali.py"),
]

# PIPELINE EXECUTION
for script in scripts:
    print("\n==============================")
    print(f" Running {os.path.basename(script)} ...")
    print("==============================\n")

    result = subprocess.run(["python3", script])

    if result.returncode != 0:
        print(f"\nERROR: {os.path.basename(script)} failed (exit code {result.returncode}).")
        print("Stopping pipeline.\n")
        break

    print(f"✔ Finished: {os.path.basename(script)}\n")

else:
    print("\n=======================================")
    print(" CALIBRATION PIPELINE IS COMPLETED  ")
    print("=======================================\n")
