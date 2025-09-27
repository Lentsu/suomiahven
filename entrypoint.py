import os
import subprocess
import sys
import time
from datetime import datetime

STAMP_FILE = "/app/.last_update"
UPDATE_INTERVAL = 7 * 24 * 60 * 60  # 7 päivää sekunteina


def run_cmd(cmd, quiet=False):
    if not quiet:
        print(f"[entrypoint] Running: {' '.join(cmd)}", flush=True)
    result = subprocess.run(cmd, check=False)
    return result.returncode


def should_update() -> bool:
    if not os.path.exists(STAMP_FILE):
        return True
    try:
        with open(STAMP_FILE) as f:
            last = int(f.read().strip())
        return (time.time() - last) >= UPDATE_INTERVAL
    except Exception:
        # Jos leima on rikki, päivitä varmuuden vuoksi
        return True


def mark_updated():
    with open(STAMP_FILE, "w") as f:
        f.write(str(int(time.time())))


def update_deps():
    if not os.path.exists("requirements.txt"):
        print("[entrypoint] requirements.txt not found – skipping updates.", flush=True)
        return

    print("[entrypoint] Checking & updating Python deps…", flush=True)
    run_cmd([sys.executable, "-m", "pip", "install", "--no-cache-dir", "--upgrade", "pip"], quiet=True)
    run_cmd([sys.executable, "-m", "pip", "install", "--no-cache-dir", "-r", "requirements.txt"])

    # Tarkista vanhentuneet paketit
    proc = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--outdated", "--format=freeze"],
        capture_output=True,
        text=True,
        check=False,
    )
    outdated = proc.stdout.strip()
    if outdated:
        print("[entrypoint] Outdated packages detected:", flush=True)
        print(outdated, flush=True)
        for line in outdated.splitlines():
            pkg = line.split("=", 1)[0]
            if pkg:
                run_cmd([sys.executable, "-m", "pip", "install", "--no-cache-dir", "-U", pkg])
    else:
        print("[entrypoint] No outdated packages.", flush=True)

    # Varmistustarkistus (ei kaada käynnistystä vaikka varoituksia)
    run_cmd([sys.executable, "-m", "pip", "check"])
    mark_updated()


def main_loop():
    while True:
        if should_update():
            update_deps()
        else:
            print("[entrypoint] Dependencies update not needed yet.", flush=True)

        print("[entrypoint] Launching bot…", flush=True)
        code = run_cmd([sys.executable, "main.py"])
        print(f"[entrypoint] Bot exited with code {code}. Restarting in 10s…", flush=True)
        time.sleep(10)


if __name__ == "__main__":
    print(f"[entrypoint] Starting container at {datetime.utcnow().isoformat()}Z", flush=True)
    main_loop()
