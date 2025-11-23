# log_comparator/gui.py

import tkinter as tk
from tkinter import ttk, filedialog as fd, messagebox
import threading
import os
import sys  # Potrzebny do funkcji pomocniczej
import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# UWAGA: Te importy mogą być podkreślone jako błąd w edytorze, ale są poprawne dla działania aplikacji
from reporting import Reporter, InterruptedException
from core import DiffEngine
from localization import Localization, SUPPORTED_LANGUAGES


# --- FUNKCJA POMOCNICZA DLA PYINSTALLER (wklejona bezpośrednio tutaj dla uproszczenia) ---
def resource_path(relative_path):
    """Zwraca absolutną ścieżkę do zasobu, działa dla trybu dev i dla PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class GuiApp:
    def __init__(self, loc: Localization, templates_path: str, locales_path: str):
        # --- POPRAWKA: Tworzymy nowy, poprawny obiekt tłumaczeń specjalnie dla GUI ---
        # Używamy przekazanego języka, ale sami znajdujemy ścieżkę do plików.
        self.loc = Localization(loc.language, locales_path=resource_path("locales"))

        self.templates_path = templates_path
        self.locales_path = locales_path
        self.root = tk.Tk()
        self.root.title(self.loc.get_string("app_title"))
        self.root.geometry("650x520")
        self.root.minsize(600, 480)

        self.cancel_event = threading.Event()
        self.is_running = False

        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=6)
        self.style.configure("Accent.TButton", foreground="white", background="#007bff")
        self.style.configure(
            "Secondary.TButton", foreground="white", background="#6c757d"
        )
        self.style.configure("Stop.TButton", foreground="white", background="#dc3545")

        main_frame = ttk.Frame(self.root, padding=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)

        self.src_var, self.out_var = tk.StringVar(), tk.StringVar()
        self.lang_var = tk.StringVar(value=self.loc.language)
        self.format_var = tk.StringVar(value="html")

        title_label = ttk.Label(
            main_frame,
            text=self.loc.get_string("main_header"),
            font=("Segoe UI", 16, "bold"),
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        ttk.Label(
            main_frame, text=self.loc.get_string("log_dir_label"), font=("Segoe UI", 10)
        ).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.src_var, width=50).grid(
            row=1, column=1, sticky=tk.EW, pady=5, padx=5
        )
        ttk.Button(
            main_frame, text=self.loc.get_string("browse_btn"), command=self._browse_src
        ).grid(row=1, column=2, pady=5)

        ttk.Label(
            main_frame,
            text=self.loc.get_string("output_dir_label"),
            font=("Segoe UI", 10),
        ).grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.out_var, width=50).grid(
            row=2, column=1, sticky=tk.EW, pady=5, padx=5
        )
        ttk.Button(
            main_frame, text=self.loc.get_string("browse_btn"), command=self._browse_out
        ).grid(row=2, column=2, pady=5)


# log_comparator/gui.py

import tkinter as tk
from tkinter import ttk, filedialog as fd, messagebox
import threading
import os
import sys  # Potrzebny do funkcji pomocniczej
import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# UWAGA: Te importy mogą być podkreślone jako błąd w edytorze, ale są poprawne dla działania aplikacji
from reporting import Reporter, InterruptedException
from core import DiffEngine
from localization import Localization, SUPPORTED_LANGUAGES


# --- FUNKCJA POMOCNICZA DLA PYINSTALLER (wklejona bezpośrednio tutaj dla uproszczenia) ---
def resource_path(relative_path):
    """Zwraca absolutną ścieżkę do zasobu, działa dla trybu dev i dla PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class GuiApp:
    def __init__(self, loc: Localization, templates_path: str, locales_path: str):
        # --- POPRAWKA: Tworzymy nowy, poprawny obiekt tłumaczeń specjalnie dla GUI ---
        # Używamy przekazanego języka, ale sami znajdujemy ścieżkę do plików.
        self.loc = Localization(loc.language, locales_path=resource_path("locales"))

        self.templates_path = templates_path
        self.locales_path = locales_path
        self.root = tk.Tk()
        self.root.title(self.loc.get_string("app_title"))
        self.root.geometry("650x520")
        self.root.minsize(600, 480)

        self.cancel_event = threading.Event()
        self.is_running = False

        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=6)
        self.style.configure("Accent.TButton", foreground="white", background="#007bff")
        self.style.configure(
            "Secondary.TButton", foreground="white", background="#6c757d"
        )
        self.style.configure("Stop.TButton", foreground="white", background="#dc3545")

        main_frame = ttk.Frame(self.root, padding=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)

        self.src_var, self.out_var = tk.StringVar(), tk.StringVar()
        self.lang_var = tk.StringVar(value=self.loc.language)
        self.format_var = tk.StringVar(value="html")

        title_label = ttk.Label(
            main_frame,
            text=self.loc.get_string("main_header"),
            font=("Segoe UI", 16, "bold"),
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        ttk.Label(
            main_frame, text=self.loc.get_string("log_dir_label"), font=("Segoe UI", 10)
        ).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.src_var, width=50).grid(
            row=1, column=1, sticky=tk.EW, pady=5, padx=5
        )
        ttk.Button(
            main_frame, text=self.loc.get_string("browse_btn"), command=self._browse_src
        ).grid(row=1, column=2, pady=5)

        ttk.Label(
            main_frame,
            text=self.loc.get_string("output_dir_label"),
            font=("Segoe UI", 10),
        ).grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.out_var, width=50).grid(
            row=2, column=1, sticky=tk.EW, pady=5, padx=5
        )
        ttk.Button(
            main_frame, text=self.loc.get_string("browse_btn"), command=self._browse_out
        ).grid(row=2, column=2, pady=5)

        ttk.Label(main_frame, text="Language:", font=("Segoe UI", 10)).grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        ttk.OptionMenu(
            main_frame,
            self.lang_var,
            self.loc.language,
            *SUPPORTED_LANGUAGES.keys(),
            command=self._on_lang_change,
        ).grid(row=3, column=1, sticky=tk.W, padx=5)

        ttk.Label(main_frame, text="Output Format:", font=("Segoe UI", 10)).grid(
            row=4, column=0, sticky=tk.W, pady=5
        )
        ttk.Combobox(
            main_frame,
            textvariable=self.format_var,
            values=["html", "pdf", "json"],
            state="readonly",
        ).grid(row=4, column=1, sticky=tk.W, padx=5)

        self.generate_btn = ttk.Button(
            main_frame,
            text=self.loc.get_string("generate_report_btn"),
            command=self._generate,
            style="Accent.TButton",
        )
        self.generate_btn.grid(
            row=5,
            column=0,
            columnspan=2,
            pady=(20, 5),
            ipady=5,
            sticky=tk.EW,
            padx=(0, 5),
        )

        self.csv_btn = ttk.Button(
            main_frame,
            text="Export CSV",
            command=self._export_csv,
            style="Secondary.TButton",
        )
        self.csv_btn.grid(row=5, column=2, pady=(20, 5), ipady=5, sticky=tk.EW)

        self.compare_btn = ttk.Button(
            main_frame,
            text=self.loc.get_string("compare_files_btn"),
            command=self._compare_files,
            style="Secondary.TButton",
        )
        self.compare_btn.grid(
            row=6,
            column=0,
            columnspan=2,
            pady=(5, 15),
            ipady=5,
            sticky=tk.EW,
            padx=(0, 5),
        )

        self.vscode_btn = ttk.Button(
            main_frame,
            text="Open in VS Code",
            command=self._open_vscode,
            style="Secondary.TButton",
        )
        self.vscode_btn.grid(row=6, column=2, pady=(5, 15), ipady=5, sticky=tk.EW)

        self.status_var = tk.StringVar(value=self.loc.get_string("ready_status"))
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN, padding=2)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(status_frame, textvariable=self.status_var, anchor=tk.W).pack(
            fill=tk.X, padx=5
        )
        self.progressbar = ttk.Progressbar(status_frame, mode="indeterminate")
        self.progressbar.pack(fill=tk.X, padx=5, pady=(0, 2))
        self.progressbar.pack_forget()

    def _toggle_ui_state(self, is_running: bool):
        self.is_running = is_running
        state = tk.DISABLED if is_running else tk.NORMAL
        if is_running:
            self.generate_btn.config(
                text=self.loc.get_string("stop_btn"),
                command=self._stop_generation,
                style="Stop.TButton",
            )
        else:
            self.generate_btn.config(
                text=self.loc.get_string("generate_report_btn"),
                command=self._generate,
                style="Accent.TButton",
            )
        self.compare_btn.config(state=state)
        self.csv_btn.config(state=state)
        self.vscode_btn.config(state=state)
        for child in self.root.winfo_children()[0].winfo_children():
            if (
                isinstance(child, (ttk.Entry, ttk.Button, ttk.OptionMenu, ttk.Combobox))
                and child != self.generate_btn
            ):
                child.config(state=state)

    def _generate(self):
        src_path, out_path = self.src_var.get().strip(), self.out_var.get().strip()
        if not src_path or not out_path:
            messagebox.showerror(
                self.loc.get_string("error_dialog_title"),
                "Please select both log and output directories!",
            )
            return
        self.cancel_event.clear()
        self._toggle_ui_state(True)
        self.status_var.set(self.loc.get_string("generating_status"))
        self.progressbar.pack(fill=tk.X, padx=5, pady=(0, 2))
        self.progressbar.start()
        threading.Thread(
            target=self._run_generation,
            args=(src_path, out_path, self.format_var.get()),
            daemon=True,
        ).start()

    def _export_csv(self):
        src_path, out_path = self.src_var.get().strip(), self.out_var.get().strip()
        if not src_path or not out_path:
            messagebox.showerror(
                self.loc.get_string("error_dialog_title"),
                "Please select both log and output directories!",
            )
            return
        self.cancel_event.clear()
        self._toggle_ui_state(True)
        self.status_var.set("Generating CSV...")
        self.progressbar.pack(fill=tk.X, padx=5, pady=(0, 2))
        self.progressbar.start()
        threading.Thread(
            target=self._run_csv_export, args=(src_path, out_path), daemon=True
        ).start()

    def _run_csv_export(self, src_path, out_path):
        try:
            reporter = Reporter(
                Path(src_path),
                Path(out_path),
                self.loc,
                self.templates_path,
                self.locales_path,
                "csv",
                self.cancel_event,
            )
            csv_path = reporter.export_csv()
            if not self.cancel_event.is_set():
                self.root.after(0, self._on_generation_success, csv_path)
        except InterruptedException:
            self.root.after(0, self._on_generation_cancelled)
        except Exception as e:
            self.root.after(0, self._on_generation_error, e)

    def _stop_generation(self):
        if self.is_running:
            self.status_var.set(self.loc.get_string("stopping_status"))
            self.cancel_event.set()

    def _run_generation(self, src_path, out_path, output_format):
        try:
            reporter = Reporter(
                Path(src_path),
                Path(out_path),
                self.loc,
                self.templates_path,
                self.locales_path,
                output_format,
                self.cancel_event,
            )
            report_path = reporter.generate()
            if not self.cancel_event.is_set():
                self.root.after(0, self._on_generation_success, report_path)
        except InterruptedException:
            self.root.after(0, self._on_generation_cancelled)
        except Exception as e:
            self.root.after(0, self._on_generation_error, e)

    def _on_generation_success(self, file_path):
        self._toggle_ui_state(False)
        self.progressbar.stop()
        self.progressbar.pack_forget()
        self.status_var.set(self.loc.get_string("success_status"))
        if messagebox.askyesno(
            self.loc.get_string("success_dialog_title"),
            self.loc.get_string("success_dialog_message", file_path=file_path),
        ):
            os.startfile(file_path)

    def _on_generation_error(self, error):
        self._toggle_ui_state(False)
        self.progressbar.stop()
        self.progressbar.pack_forget()
        error_msg = f"Error: {error}"
        self.status_var.set(self.loc.get_string("failure_status"))
        logging.exception(error_msg)
        messagebox.showerror(self.loc.get_string("error_dialog_title"), error_msg)

    def _on_generation_cancelled(self):
        self._toggle_ui_state(False)
        self.progressbar.stop()
        self.progressbar.pack_forget()
        self.status_var.set(self.loc.get_string("stopped_status"))

    def _on_lang_change(self, lang_code):
        self.root.destroy()
        from utils import resource_path

        templates_path = resource_path("templates")
        locales_path = resource_path("locales")
        app = GuiApp(
            Localization(lang_code, locales_path=locales_path),
            templates_path,
            locales_path,
        )
        app.run()

    def _browse_src(self):
        if path := fd.askdirectory(title=self.loc.get_string("log_dir_label")):
            self.src_var.set(path)

    def _browse_out(self):
        if path := fd.askdirectory(title=self.loc.get_string("output_dir_label")):
            self.out_var.set(path)

    def _compare_files(self):
        pre = fd.askopenfilename(title="Select FIRST file")
        if not pre:
            return
        post = fd.askopenfilename(title="Select SECOND file")
        if not post:
            return
        out = self.out_var.get().strip() or fd.askdirectory(
            title="Select OUTPUT directory"
        )
        if not out:
            return
        self.status_var.set(self.loc.get_string("comparing_status"))
        self.progressbar.pack(fill=tk.X, padx=5, pady=(0, 2))
        self.progressbar.start()
        threading.Thread(
            target=self._run_file_comparison, args=(pre, post, out), daemon=True
        ).start()

    def _open_vscode(self):
        pre = fd.askopenfilename(title="Select FIRST file")
        if not pre:
            return
        post = fd.askopenfilename(title="Select SECOND file")
        if not post:
            return

        import subprocess

        try:
            # Try to run 'code --diff'
            subprocess.Popen(["code", "--diff", pre, post], shell=True)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open VS Code: {e}")

    def _run_file_comparison(self, pre_p, post_p, out_d):
        try:
            pre, post, out = Path(pre_p), Path(post_p), Path(out_d)
            diff_result = DiffEngine().diff(
                pre.read_text(errors="ignore").splitlines(),
                post.read_text(errors="ignore").splitlines(),
            )
            diff_path = out / f"custom_diff_{pre.stem}_vs_{post.stem}.html"
            env = Environment(loader=FileSystemLoader(self.templates_path))
            template = env.get_template("diff_view.html")
            html = template.render(
                t=self.loc.get_string,
                is_custom_comparison=True,
                ip="Custom",
                pre_file=pre.name,
                post_file=post.name,
                lines=diff_result["lines"],
            )
            diff_path.write_text(html, encoding="utf-8")
            self.root.after(0, self._on_generation_success, diff_path)
        except Exception as e:
            self.root.after(0, self._on_generation_error, e)

    def run(self):
        self.root.mainloop()
