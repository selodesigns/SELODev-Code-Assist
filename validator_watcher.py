import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCH_DIR = Path("/mnt/Projects/GitHub/SELODevCodeAssist")
VALIDATOR_SCRIPT = WATCH_DIR / "code_validator.py"
VALID_EXTENSIONS = [".py", ".js", ".html"]

class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.suffix in VALID_EXTENSIONS:
            print(f"🔍 Validating: {file_path}")
            result = subprocess.run(["python3", str(VALIDATOR_SCRIPT), str(file_path)],
                                    capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(f"⚠️ Error: {result.stderr}")

if __name__ == "__main__":
    print(f"🛡️ Watching {WATCH_DIR} for changes...")
    observer = Observer()
    observer.schedule(ChangeHandler(), path=str(WATCH_DIR), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
