import time
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import os
import signal
import psutil


class CodeChangeHandler(FileSystemEventHandler):
    def __init__(self, main_script):
        self.main_script = main_script
        self.last_modified = time.time()
        self.cooldown = 1.0
        self.current_process = None

    def _kill_process_tree(self, pid):
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)

            # Kill children first
            for child in children:
                try:
                    child.terminate()
                except psutil.NoSuchProcess:
                    pass

            # Kill parent
            try:
                parent.terminate()
            except psutil.NoSuchProcess:
                pass

            # Wait for processes to terminate
            gone, alive = psutil.wait_procs(children + [parent], timeout=3)

            # Force kill if still alive
            for p in alive:
                try:
                    p.kill()
                except psutil.NoSuchProcess:
                    pass

        except psutil.NoSuchProcess:
            pass

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith(".py"):
            return

        # Implement cooldown
        current_time = time.time()
        if current_time - self.last_modified < self.cooldown:
            return
        self.last_modified = current_time

        print(f"\nFile {event.src_path} has been modified")
        print("Regenerating city...")

        # Kill previous visualization process if it exists
        if self.current_process and self.current_process.poll() is None:
            self._kill_process_tree(self.current_process.pid)

        try:
            # Start new process
            self.current_process = subprocess.Popen(
                [sys.executable, self.main_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            print("\nCity regeneration started!")
            print("\nWatching for changes...")
        except subprocess.SubprocessError as e:
            print(f"\nError regenerating city: {e}")


def watch_directory(path=".", main_script="main.py"):
    print(f"Watching directory: {path}")
    print(f"Main script: {main_script}")

    observer = Observer()
    event_handler = CodeChangeHandler(main_script)

    # Initial run
    print("Running initial generation...")
    event_handler.current_process = subprocess.Popen(
        [sys.executable, main_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    print(f"\nWatching directory '{os.path.abspath(path)}' for changes...")
    print("(Press Ctrl+C to stop)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        if event_handler.current_process:
            event_handler._kill_process_tree(event_handler.current_process.pid)
        observer.stop()
        print("\nStopping file watcher...")

    observer.join()


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = "./renderer/utils/City.py"
    src_dir = "./renderer"
    watch_directory(src_dir, main_script)
