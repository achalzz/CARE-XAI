from __future__ import annotations

import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .config import AppConfig


class TrainingJobManager:
    """Runs `backend/train.py` as a background subprocess and tracks state.

    A single job runs at a time. State and a bounded ring buffer of log lines
    are kept in memory for the dashboard to poll.
    """

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._proc: Optional[subprocess.Popen] = None
        self._state: str = "idle"
        self._started_at: Optional[str] = None
        self._finished_at: Optional[str] = None
        self._message: Optional[str] = None
        self._logs: List[str] = []
        self._lock = threading.Lock()
        self._max_logs = 200

    @property
    def is_running(self) -> bool:
        with self._lock:
            return self._proc is not None and self._proc.poll() is None

    def _append_log(self, line: str) -> None:
        with self._lock:
            self._logs.append(line)
            if len(self._logs) > self._max_logs:
                self._logs = self._logs[-self._max_logs :]

    def _poll_loop(self, proc: subprocess.Popen) -> None:
        if proc.stdout:
            for line in iter(proc.stdout.readline, ""):
                line = line.rstrip()
                if line:
                    self._append_log(line)
        if proc.stderr:
            for line in iter(proc.stderr.readline, ""):
                line = line.rstrip()
                if line:
                    self._append_log(line)
        proc.stdout.close()
        proc.stderr.close()
        code = proc.wait()
        with self._lock:
            self._finished_at = datetime.now(timezone.utc).isoformat()
            self._state = "completed" if code == 0 else "failed"
            self._message = f"Training finished with exit code {code}."
            self._proc = None

    def start(self, overrides: Optional[dict] = None) -> dict:
        with self._lock:
            if self._proc is not None and self._proc.poll() is None:
                return {
                    "state": "running",
                    "pid": self._proc.pid,
                    "message": "A training job is already running.",
                }
            self._state = "running"
            self._started_at = datetime.now(timezone.utc).isoformat()
            self._finished_at = None
            self._message = None
            self._logs = []

            cmd = [sys.executable, str(Path("backend/train.py"))]
            overrides = overrides or {}
            if overrides.get("epochs") is not None:
                cmd += ["--epochs", str(overrides["epochs"])]
            if overrides.get("batch_size") is not None:
                cmd += ["--batch-size", str(overrides["batch_size"])]
            if overrides.get("image_size") is not None:
                cmd += ["--image-size", str(overrides["image_size"])]
            if overrides.get("lr") is not None:
                cmd += ["--lr", str(overrides["lr"])]

            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding="utf-8",
                errors="replace",
            )
            self._proc = proc
            threading.Thread(target=self._poll_loop, args=(proc,), daemon=True).start()
            return {"state": "running", "pid": proc.pid, "message": "Training started."}

    def status(self) -> dict:
        with self._lock:
            proc = self._proc
            if proc is not None and proc.poll() is not None:
                self._state = "completed" if proc.returncode == 0 else "failed"
                self._message = f"Training finished with exit code {proc.returncode}."
                self._proc = None
            return {
                "state": self._state,
                "pid": proc.pid if proc is not None else None,
                "started_at": self._started_at,
                "finished_at": self._finished_at,
                "message": self._message,
                "logs": list(self._logs[-50:]),
            }
