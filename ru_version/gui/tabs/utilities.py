import tkinter as tk
from tkinter import ttk, filedialog
import json
import datetime

from gui.base_tab import BaseTab

try:
    from core.crypto_manager import generate_strong_password, calculate_file_hash
except ImportError:
    print("Ошибка импорта утилит из ядра")

class UtilitiesTab(BaseTab):
    def setup_ui(self):
        pad_frame = tk.Frame(self.main_frame)
        pad_frame.pack(fill='both', expand=True)
        
        pad_frame.columnconfigure(0, weight=1, uniform="utils")
        pad_frame.columnconfigure(1, weight=1, uniform="utils")

        # === LEFT COLUMN: PASSWORD GENERATOR ===
        f_gen = tk.LabelFrame(pad_frame, text="Генератор паролей", font=("Arial", 11, "bold"), fg="#e67e22", padx=10, pady=10)
        f_gen.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=10)

        # Length
        tk.Label(f_gen, text="Длина пароля:").pack(anchor="w")
        scale_frame = tk.Frame(f_gen)
        scale_frame.pack(fill='x', pady=5)
        
        self.lbl_len = tk.Label(scale_frame, text="24", width=3, font=("Arial", 10, "bold"))
        self.lbl_len.pack(side="right")
        
        self.scale_len = ttk.Scale(scale_frame, from_=8, to=64, orient="horizontal", command=self.update_len_lbl)
        self.scale_len.set(24)
        self.scale_len.pack(side="left", fill="x", expand=True)

        # Options
        self.var_digits = tk.BooleanVar(value=True)
        self.var_symbols = tk.BooleanVar(value=True)
        tk.Checkbutton(f_gen, text="Цифры (0-9)", variable=self.var_digits).pack(anchor="w")
        tk.Checkbutton(f_gen, text="Спецсимволы (!@#...)", variable=self.var_symbols).pack(anchor="w")

        # Generator button
        tk.Button(f_gen, text="СГЕНЕРИРОВАТЬ", bg="#ffe0b2", font=("Arial", 10, "bold"), 
                  command=self.run_generate).pack(fill='x', pady=15)

        # Result
        tk.Label(f_gen, text="Сгенерированный пароль:").pack(anchor="w")
        res_frame = tk.Frame(f_gen)
        res_frame.pack(fill='x')
        
        self.ent_pass_res = tk.Entry(res_frame, font=("Consolas", 11), fg="#d35400", justify="center")
        self.ent_pass_res.pack(side="left", fill="x", expand=True)
        tk.Button(res_frame, text="📋", width=3, command=self.copy_pass).pack(side="right", padx=(5,0))

        # === RIGHT COLUMN: HASH AND CHECK ===

        f_hash = tk.LabelFrame(pad_frame, text="Проверка целостности (SHA-256)", font=("Arial", 11, "bold"), fg="#8e44ad", padx=10, pady=10)
        f_hash.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=10)

        # File selection
        tk.Label(f_hash, text="Файл для проверки:").pack(anchor="w")
        row_file = tk.Frame(f_hash); row_file.pack(fill='x', pady=5)
        
        self.ent_file_hash = tk.Entry(row_file)
        self.ent_file_hash.pack(side="left", fill="x", expand=True)
        tk.Button(row_file, text="📂", width=3, command=lambda: self.select_file(self.ent_file_hash)).pack(side="right", padx=(5,0))

        tk.Button(f_hash, text="РАССЧИТАТЬ ХЕШ", bg="#e8daef", font=("Arial", 10, "bold"), 
                  command=self.run_hash).pack(fill='x', pady=10)

        # Hash result field
        tk.Label(f_hash, text="Рассчитанный хеш:").pack(anchor="w")
        row_res_hash = tk.Frame(f_hash); row_res_hash.pack(fill='x')
        
        self.ent_hash_result = tk.Entry(row_res_hash, font=("Consolas", 9), bg="#f4f6f7", state="readonly")
        self.ent_hash_result.pack(side="left", fill="x", expand=True)
        tk.Button(row_res_hash, text="📋", width=3, command=self.copy_hash).pack(side="right", padx=(5,0))

        # --- COMPARISON BLOCK ---
        tk.Label(f_hash, text=" ").pack() # Отступ
        tk.Label(f_hash, text="Сравнить с (вставьте хеш оригинала):").pack(anchor="w")
        
        # 1. Row with entry field (full width)
        row_check_entry = tk.Frame(f_hash)
        row_check_entry.pack(fill='x', pady=(0, 5))
        
        self.ent_hash_check = tk.Entry(row_check_entry, font=("Consolas", 9))
        self.ent_hash_check.pack(fill='x', expand=True)
        
        # 2. Row with buttons (below field)
        row_check_btns = tk.Frame(f_hash)
        row_check_btns.pack(fill='x', pady=(0, 5))
        
        
        tk.Button(row_check_btns, text="📋 Вставить", bg="#e0f7fa", 
                  command=self.paste_hash_check).pack(side="left", expand=True, fill="x", padx=(0, 2)) 
        tk.Button(row_check_btns, text="❌ Очистить", bg="#ffebee", 
                  command=self.clear_hash_check).pack(side="left", expand=True, fill="x", padx=2)     
        tk.Button(row_check_btns, text="✅ Проверить", bg="#e8f5e9", font=("Arial", 9, "bold"),
                  command=self.run_compare).pack(side="left", expand=True, fill="x", padx=(2, 0))

        # Comparison result label
        self.lbl_compare_res = tk.Label(f_hash, text="", font=("Arial", 12, "bold"))
        self.lbl_compare_res.pack(pady=5)

        # === BOTTOM BLOCK: MASTER EXPORT ===

        f_export = tk.Frame(pad_frame, pady=10)
        f_export.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        btn_master = tk.Button(f_export, text="💾 ПОЛНЫЙ ЭКСПОРТ СЕССИИ (Пароль + Настройки + Хеш)", 
                               bg="#ffecb3", fg="#d35400", font=("Arial", 10, "bold"),
                               command=self.run_master_export)
        btn_master.pack(fill='x', padx=10)
        
        tk.Label(f_export, text="Внимание: этот файл содержит ваш пароль в открытом виде! Храните его в безопасном месте.", 
                 fg="red", font=("Arial", 8)).pack()

        self.add_console_widget()

    # --- METHODS ---

    def update_len_lbl(self, val):
        self.lbl_len.config(text=str(int(float(val))))

    def select_file(self, w):
        f = filedialog.askopenfilename()
        if f: w.delete(0, tk.END); w.insert(0, f)

    def copy_pass(self):
        pwd = self.ent_pass_res.get()
        if pwd:
            self.clipboard_clear()
            self.clipboard_append(pwd)
            self.update()
            self.write_log("Пароль скопирован.")

    def copy_hash(self):
        h = self.ent_hash_result.get()
        if h:
            self.clipboard_clear()
            self.clipboard_append(h)
            self.update()
            self.write_log("Хеш скопирован.")

    def run_generate(self):
        length = int(self.scale_len.get())
        use_dig = self.var_digits.get()
        use_sym = self.var_symbols.get()

        try:
            pwd = generate_strong_password(length, use_dig, use_sym)
            self.ent_pass_res.delete(0, tk.END)
            self.ent_pass_res.insert(0, pwd)
            self.write_log(f"Сгенерирован пароль длиной {length}.")
        except Exception as e:
            self.write_log(f"Ошибка генерации: {e}", is_error=True)

    def run_hash(self):
        path = self.ent_file_hash.get().strip()
        if not path:
            self.write_log("Выберите файл для хеширования!", is_error=True)
            return

        try:
            self.write_log(f"Вычисление SHA-256 для: {path} ...")
            self.update_idletasks() 
            
            h = calculate_file_hash(path)
            
            self.ent_hash_result.config(state="normal")
            self.ent_hash_result.delete(0, tk.END)
            self.ent_hash_result.insert(0, h)
            self.ent_hash_result.config(state="readonly")
            
            self.write_log(f"Хеш успешно вычислен.")
        except Exception as e:
            self.write_log(f"Ошибка хеширования: {e}", is_error=True)

    def run_compare(self):
        """Hash comparison logic"""
        calculated = self.ent_hash_result.get().strip()
        expected = self.ent_hash_check.get().strip()

        if not calculated:
            self.write_log("Сначала рассчитайте хеш файла!", is_error=True)
            return
        if not expected:
            self.write_log("Введите хеш оригинала для сравнения!", is_error=True)
            return

        # Case-insensitive comparison
        if calculated.lower() == expected.lower():
            self.lbl_compare_res.config(text="✔ ХЕШИ СОВПАДАЮТ", fg="green")
            self.write_log("Результат сравнения: СОВПАДЕНИЕ (Файл цел)")
        else:
            self.lbl_compare_res.config(text="❌ НЕ СОВПАДАЮТ!", fg="red")
            self.write_log("Результат сравнения: ОШИБКА! Хеши различаются.", is_error=True)

    def run_master_export(self):
        """Export everything: config, password and hash"""
        if not self.app.app_config:
            self.write_log("Настройки шифрования пусты.", is_error=True)
            return

        data_to_export = self.app.app_config.copy()
        
        # Add data from this tab
        pwd = self.ent_pass_res.get().strip()
        file_hash = self.ent_hash_result.get().strip()
        
        # Add to dict. 
        # IMPORTANT: These keys won't interfere with SettingsTab import, as it won't read them.
        if pwd:
            data_to_export["generated_password"] = pwd
        if file_hash:
            data_to_export["calculated_file_hash"] = file_hash
            
        data_to_export["export_date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save
        filename = filedialog.asksaveasfilename(
            defaultextension=".json", 
            filetypes=[("Master JSON", "*.json")],
            title="Сохранить полный бэкап сессии"
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data_to_export, f, indent=4)
                
                self.write_log(f"Полный экспорт сохранен: {filename}")
                self.write_log("ВНИМАНИЕ: Этот файл содержит пароль. Не передавайте его по открытым каналам!", is_error=True)
            except Exception as e:
                self.write_log(f"Ошибка сохранения: {e}", is_error=True)
    
    def paste_hash_check(self):
        """Inserts text from clipboard to comparison field"""
        try:
            # Get text from clipboard
            text = self.clipboard_get()
            
            # Clear field and insert
            self.ent_hash_check.delete(0, tk.END)
            self.ent_hash_check.insert(0, text)
            
            # Reset old check result
            self.lbl_compare_res.config(text="")
        except tk.TclError:
            # If buffer empty or image, do nothing
            pass

    def clear_hash_check(self):
        """Clears comparison field and result"""
        self.ent_hash_check.delete(0, tk.END)
        self.lbl_compare_res.config(text="")