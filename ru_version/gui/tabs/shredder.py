import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os

from gui.base_tab import BaseTab

try:
    from core.shredder_manager import wipe_file, wipe_directory
except ImportError:
    print("Ошибка импорта шредера")

class ShredderTab(BaseTab):
    def setup_ui(self):
        # Container
        pad = tk.Frame(self.main_frame)
        pad.pack(fill='both', expand=True)
        
        # Center content
        center = tk.Frame(pad)
        center.pack(expand=True, fill='x', padx=50)

        # TITLE
        tk.Label(center, text="⚠️ БЕЗВОЗВРАТНОЕ УДАЛЕНИЕ ⚠️", 
                 font=("Arial", 16, "bold"), fg="red").pack(pady=(0, 5))

        # === SELECTION BLOCK ===
        f_select = tk.LabelFrame(center, text="Что удаляем?", font=("Arial", 11, "bold"), padx=15, pady=5)
        f_select.pack(fill='x', pady=5)

        # Radiobuttons (File / Folder)
        self.mode_var = tk.StringVar(value="file")
        
        frame_radio = tk.Frame(f_select)
        frame_radio.pack(anchor="w", pady=5)
        
        tk.Radiobutton(frame_radio, text="Одиночный файл", variable=self.mode_var, 
                       value="file", command=self.toggle_mode).pack(side="left", padx=(0, 20))
        tk.Radiobutton(frame_radio, text="Всю папку", variable=self.mode_var, 
                       value="folder", command=self.toggle_mode).pack(side="left")

        # Input field
        self.row_input = tk.Frame(f_select)
        self.row_input.pack(fill='x', pady=5)
        
        self.ent_path = tk.Entry(self.row_input, font=("Arial", 10))
        self.ent_path.pack(side="left", fill="x", expand=True)
        
        self.btn_browse = tk.Button(self.row_input, text="📂 Выбрать файл", command=self.browse)
        self.btn_browse.pack(side="right", padx=(5, 0))


        # === DELETION SETTINGS ===
        f_opts = tk.LabelFrame(center, text="Метод удаления", font=("Arial", 11, "bold"), padx=15, pady=5)
        f_opts.pack(fill='x', pady=5)

        tk.Label(f_opts, text="Количество проходов (перезаписей):").pack(anchor="w")
        
        # Slider (1 - 7)
        self.scale_passes = tk.Scale(f_opts, from_=1, to=7, orient="horizontal", tickinterval=1)
        self.scale_passes.set(1) # Default 1 (fast)
        self.scale_passes.pack(fill='x', pady=5)
        
        # Explanation
        self.lbl_info = tk.Label(f_opts, text="1 проход: Быстро (Нули). Достаточно для большинства задач.\n3 прохода: Стандарт DoD (Надежно).\n7 проходов: Параноидальный режим (Медленно).", 
                                 justify="left", fg="#555", font=("Arial", 9))
        self.lbl_info.pack(anchor="w", pady=5)


        # === RUN BUTTON ===
        self.btn_shred = tk.Button(center, text="УНИЧТОЖИТЬ ДАННЫЕ", bg="#b71c1c", fg="white", 
                                   font=("Arial", 12, "bold"), height=2,
                                   command=self.confirm_and_run)
        self.btn_shred.pack(fill='x', pady=[10, 5])

        self.add_console_widget()

    # --- METHODS ---

    def toggle_mode(self):
        mode = self.mode_var.get()
        if mode == "file":
            self.btn_browse.config(text="📂 Выбрать файл")
        else:
            self.btn_browse.config(text="📂 Выбрать папку")

    def browse(self):
        mode = self.mode_var.get()
        if mode == "file":
            path = filedialog.askopenfilename()
        else:
            path = filedialog.askdirectory()
        
        if path:
            self.ent_path.delete(0, tk.END)
            self.ent_path.insert(0, path)

    def confirm_and_run(self):
        path = self.ent_path.get().strip()
        passes = self.scale_passes.get()
        mode = self.mode_var.get()

        if not path:
            self.write_log("Выберите файл или папку!", is_error=True)
            return
        
        if not os.path.exists(path):
            self.write_log("Объект не существует (уже удален?)", is_error=True)
            return

        # CONFIRMATION DIALOG
        msg = f"Вы уверены, что хотите БЕЗВОЗВРАТНО удалить:\n\n{path}\n\nВосстановление будет НЕВОЗМОЖНО."
        if messagebox.askyesno("ПОДТВЕРЖДЕНИЕ УНИЧТОЖЕНИЯ", msg, icon='warning', default='no'):
            # Run in thread
            threading.Thread(target=self.run_worker, args=(path, passes, mode), daemon=True).start()

    def run_worker(self, path, passes, mode):
        def cb(msg, is_error=False):
            self.write_log(msg, is_error)

        try:
            self.btn_shred.config(state="disabled", text="УДАЛЕНИЕ...")
            self.write_log(f"--- НАЧАЛО УНИЧТОЖЕНИЯ ({passes} проходов) ---")
            
            if mode == "file":
                wipe_file(path, passes, status_callback=cb)
            else:
                wipe_directory(path, passes, status_callback=cb)
            
            self.write_log(f"ОБЪЕКТ УНИЧТОЖЕН: {path}")
            
            # Clear input field so not to press again accidentally
            self.after(0, lambda: self.ent_path.delete(0, tk.END))

        except Exception as e:
            self.write_log(f"Ошибка: {e}", is_error=True)
        finally:
            self.after(0, lambda: self.btn_shred.config(state="normal", text="УНИЧТОЖИТЬ ДАННЫЕ"))