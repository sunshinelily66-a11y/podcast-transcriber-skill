import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


ROOT = Path(__file__).resolve().parent
PIPELINE = ROOT / "scripts" / "run_pipeline.py"


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Podcast Transcriber")
        self.geometry("900x650")

        self.proc: subprocess.Popen | None = None
        self.log_queue: queue.Queue[str] = queue.Queue()

        self.input_mode = tk.StringVar(value="file")
        self.file_path = tk.StringVar()
        self.url_value = tk.StringVar()
        self.model = tk.StringVar(value="tiny")
        self.language = tk.StringVar(value="en")
        self.summarize = tk.BooleanVar(value=True)
        self.highlights = tk.BooleanVar(value=False)

        self._build_ui()
        self.after(200, self._drain_logs)

    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": 6}

        top = ttk.Frame(self)
        top.pack(fill="x", **pad)

        ttk.Label(top, text="Input Mode").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(top, text="Local File", variable=self.input_mode, value="file", command=self._toggle_input).grid(
            row=0, column=1, sticky="w"
        )
        ttk.Radiobutton(top, text="URL (RSS / audio)", variable=self.input_mode, value="url", command=self._toggle_input).grid(
            row=0, column=2, sticky="w"
        )

        self.file_frame = ttk.Frame(self)
        self.file_frame.pack(fill="x", **pad)
        ttk.Label(self.file_frame, text="Audio File").pack(side="left")
        self.file_entry = ttk.Entry(self.file_frame, textvariable=self.file_path, width=80)
        self.file_entry.pack(side="left", fill="x", expand=True, padx=8)
        ttk.Button(self.file_frame, text="Browse", command=self._browse_file).pack(side="left")

        self.url_frame = ttk.Frame(self)
        ttk.Label(self.url_frame, text="URL").pack(side="left")
        self.url_entry = ttk.Entry(self.url_frame, textvariable=self.url_value, width=100)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=8)

        opts = ttk.Frame(self)
        opts.pack(fill="x", **pad)
        ttk.Label(opts, text="Model").grid(row=0, column=0, sticky="w")
        ttk.Combobox(opts, textvariable=self.model, values=["tiny", "base", "small"], width=10, state="readonly").grid(
            row=0, column=1, sticky="w", padx=8
        )
        ttk.Label(opts, text="Language").grid(row=0, column=2, sticky="w")
        ttk.Entry(opts, textvariable=self.language, width=10).grid(row=0, column=3, sticky="w", padx=8)
        ttk.Checkbutton(opts, text="Summary (CN)", variable=self.summarize).grid(row=0, column=4, sticky="w", padx=8)
        ttk.Checkbutton(opts, text="Highlights (CN)", variable=self.highlights).grid(row=0, column=5, sticky="w", padx=8)

        actions = ttk.Frame(self)
        actions.pack(fill="x", **pad)
        self.run_btn = ttk.Button(actions, text="Run", command=self._run_pipeline)
        self.run_btn.pack(side="left")
        self.stop_btn = ttk.Button(actions, text="Stop", command=self._stop_pipeline, state="disabled")
        self.stop_btn.pack(side="left", padx=8)
        ttk.Button(actions, text="Open downloads", command=lambda: self._open_folder(ROOT / "downloads")).pack(side="left", padx=8)
        ttk.Button(actions, text="Open transcripts", command=lambda: self._open_folder(ROOT / "transcripts")).pack(side="left", padx=8)
        ttk.Button(actions, text="Open summaries", command=lambda: self._open_folder(ROOT / "summaries")).pack(side="left", padx=8)
        ttk.Button(actions, text="Open highlights", command=lambda: self._open_folder(ROOT / "highlights")).pack(side="left", padx=8)

        ttk.Label(self, text="Log").pack(anchor="w", padx=10)
        self.log = tk.Text(self, wrap="word", height=28)
        self.log.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._toggle_input()

    def _toggle_input(self) -> None:
        self.url_frame.pack_forget()
        self.file_frame.pack_forget()
        if self.input_mode.get() == "file":
            self.file_frame.pack(fill="x", padx=10, pady=6)
        else:
            self.url_frame.pack(fill="x", padx=10, pady=6)

    def _browse_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio files", "*.mp3 *.m4a *.wav *.aac *.ogg"), ("All files", "*.*")],
        )
        if path:
            self.file_path.set(path)

    def _append_log(self, text: str) -> None:
        self.log.insert("end", text)
        self.log.see("end")

    def _drain_logs(self) -> None:
        while not self.log_queue.empty():
            self._append_log(self.log_queue.get())
        self.after(200, self._drain_logs)

    def _run_pipeline(self) -> None:
        if self.proc is not None:
            messagebox.showwarning("Busy", "A job is already running.")
            return

        cmd = [sys.executable, str(PIPELINE)]
        if self.input_mode.get() == "file":
            path = self.file_path.get().strip()
            if not path:
                messagebox.showerror("Missing input", "Please choose a local audio file.")
                return
            cmd += ["--input", path]
        else:
            url = self.url_value.get().strip()
            if not url:
                messagebox.showerror("Missing URL", "Please enter an RSS/audio URL.")
                return
            cmd += ["--url", url]

        cmd += ["--model", self.model.get(), "--language", self.language.get().strip() or "en"]
        if self.summarize.get():
            cmd.append("--summarize")
        elif self.highlights.get():
            cmd.append("--highlights")

        env = os.environ.copy()
        env.setdefault("PYTHONIOENCODING", "utf-8")

        self._append_log("\n=== Start ===\n")
        self._append_log("[run] " + " ".join(cmd) + "\n")
        self.run_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        def worker() -> None:
            try:
                self.proc = subprocess.Popen(
                    cmd,
                    cwd=str(ROOT),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    env=env,
                )
                assert self.proc.stdout is not None
                for line in self.proc.stdout:
                    self.log_queue.put(line)
                code = self.proc.wait()
                self.log_queue.put(f"\n[exit] code={code}\n")
            except Exception as e:
                self.log_queue.put(f"\n[error] {e}\n")
            finally:
                self.proc = None
                self.after(0, self._on_finish)

        threading.Thread(target=worker, daemon=True).start()

    def _on_finish(self) -> None:
        self.run_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def _stop_pipeline(self) -> None:
        if self.proc is not None:
            try:
                self.proc.terminate()
                self._append_log("\n[info] terminate requested\n")
            except Exception as e:
                self._append_log(f"\n[warn] failed to terminate: {e}\n")

    def _open_folder(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        try:
            os.startfile(str(path))  # type: ignore[attr-defined]
        except Exception as e:
            messagebox.showerror("Open folder failed", str(e))


if __name__ == "__main__":
    App().mainloop()

