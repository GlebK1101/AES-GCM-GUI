import tkinter as tk
from tkinter import filedialog
from cryptography.exceptions import InvalidTag 
from gui.base_tab import BaseTab

try:
    from core.crypto_manager import encrypt_file, decrypt_file
except ImportError:
    def encrypt_file(**kwargs): pass
    def decrypt_file(**kwargs): pass
    print("Внимание: core.crypto_manager не найден.")

class EncryptionTab(BaseTab):
    def setup_ui(self):
        # Variable for "Hide password" checkbox
        self.is_password_hidden = tk.BooleanVar(value=False)

        # Container with padding
        pad_frame = tk.Frame(self.main_frame)
        pad_frame.pack(fill='both', expand=True)

        # --- HIDE PASSWORD CHECKBOX ---
        chk_hide = tk.Checkbutton(pad_frame, text="Скрывать пароль", 
                                  variable=self.is_password_hidden, 
                                  command=self.toggle_password)
        chk_hide.pack(anchor="w", pady=(0, 10))

        # --- COLUMN SPLIT ---
        top_frame = tk.Frame(pad_frame)
        top_frame.pack(fill='x', pady=(0, 20))
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)

        # === LEFT COLUMN: ENCRYPTION ===
        frame_enc = tk.LabelFrame(top_frame, text="Шифрование", font=("Arial", 12, "bold"), fg="blue", padx=10, pady=10)
        frame_enc.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # 1. Input file
        tk.Label(frame_enc, text="Файл:").pack(anchor="w")
        f_enc_file = tk.Frame(frame_enc)
        f_enc_file.pack(fill='x', pady=(0, 5))
        
        self.ent_enc_path = tk.Entry(f_enc_file)
        self.ent_enc_path.pack(side="left", fill="x", expand=True)
        tk.Button(f_enc_file, text="📂", width=3, 
                  command=lambda: self.select_file(self.ent_enc_path)).pack(side="right", padx=(5, 0))

        # 2. Output folder
        tk.Label(frame_enc, text="Папка сохранения (по умолч. рядом):").pack(anchor="w")
        f_enc_out = tk.Frame(frame_enc)
        f_enc_out.pack(fill='x', pady=(0, 5))
        
        self.ent_enc_out = tk.Entry(f_enc_out)
        self.ent_enc_out.pack(side="left", fill="x", expand=True)
        tk.Button(f_enc_out, text="📂", width=3, 
                  command=lambda: self.select_folder(self.ent_enc_out)).pack(side="right", padx=(5, 0))

        # 3. FILENAME 
        tk.Label(frame_enc, text="Имя выходного файла (опц., без .enc):").pack(anchor="w")
        
        row_name_enc = tk.Frame(frame_enc)
        row_name_enc.pack(fill='x', pady=(0, 5))
        
        self.ent_enc_name = tk.Entry(row_name_enc)
        self.ent_enc_name.pack(side="left", fill="x", expand=True)

        tk.Button(row_name_enc, text="📋", width=3, 
                  command=lambda: self.paste_entry(self.ent_enc_name)).pack(side="right", padx=(5, 0))
        
        # 4. Password
        tk.Label(frame_enc, text="Пароль:").pack(anchor="w")
        self.ent_enc_pass = tk.Entry(frame_enc, show="") 
        self.ent_enc_pass.pack(fill='x', pady=(0, 5))
        
        # Row of password buttons
        row_pass_tools_enc = tk.Frame(frame_enc)
        row_pass_tools_enc.pack(fill='x', pady=(0, 15))
        
        tk.Button(row_pass_tools_enc, text="📋 Вставить", font=("Arial", 8), bg="#e0f7fa",
                  command=lambda: self.paste_entry(self.ent_enc_pass)).pack(side="left", expand=True, fill="x", padx=(0,1))
        tk.Button(row_pass_tools_enc, text="📑 Копировать", font=("Arial", 8),
                  command=lambda: self.copy_entry(self.ent_enc_pass)).pack(side="left", expand=True, fill="x", padx=1)
        tk.Button(row_pass_tools_enc, text="❌ Очистить", font=("Arial", 8), bg="#ffebee",
                  command=lambda: self.clear_entry(self.ent_enc_pass)).pack(side="left", expand=True, fill="x", padx=(1,0))

        # 5. Run button
        tk.Button(frame_enc, text="ЗАШИФРОВАТЬ", bg="#ffcccc", font=("Arial", 12, "bold"),
                  command=self.on_encrypt_click).pack(side="bottom", fill='x', pady=5)

        # === RIGHT COLUMN: DECRYPTION ===

        frame_dec = tk.LabelFrame(top_frame, text="Дешифрование", font=("Arial", 12, "bold"), fg="green", padx=10, pady=10)
        frame_dec.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # 1. Input file
        tk.Label(frame_dec, text="Файл (.enc):").pack(anchor="w")
        f_dec_file = tk.Frame(frame_dec)
        f_dec_file.pack(fill='x', pady=(0, 5))
        
        self.ent_dec_path = tk.Entry(f_dec_file)
        self.ent_dec_path.pack(side="left", fill="x", expand=True)
        tk.Button(f_dec_file, text="📂", width=3, 
                  command=lambda: self.select_file(self.ent_dec_path)).pack(side="right", padx=(5, 0))

        # 2. Output folder
        tk.Label(frame_dec, text="Папка сохранения (по умолч. рядом):").pack(anchor="w")
        f_dec_out = tk.Frame(frame_dec)
        f_dec_out.pack(fill='x', pady=(0, 5))
        
        self.ent_dec_out = tk.Entry(f_dec_out)
        self.ent_dec_out.pack(side="left", fill="x", expand=True)
        tk.Button(f_dec_out, text="📂", width=3, 
                  command=lambda: self.select_folder(self.ent_dec_out)).pack(side="right", padx=(5, 0))
        
        # 3. SPACER
        tk.Label(frame_dec, text=" ").pack(anchor="w") 
        tk.Entry(frame_dec, state="disabled", relief="flat", bg=frame_dec.cget("bg")).pack(fill='x', pady=(0, 12))
        
        # 4. Password
        tk.Label(frame_dec, text="Пароль:").pack(anchor="w")
        self.ent_dec_pass = tk.Entry(frame_dec, show="")
        self.ent_dec_pass.pack(fill='x', pady=(0, 5))

        # Row of password buttons
        row_pass_tools_dec = tk.Frame(frame_dec)
        row_pass_tools_dec.pack(fill='x', pady=(0, 15))
        
        tk.Button(row_pass_tools_dec, text="📋 Вставить", font=("Arial", 8), bg="#e0f7fa",
                  command=lambda: self.paste_entry(self.ent_dec_pass)).pack(side="left", expand=True, fill="x", padx=(0,1))
        tk.Button(row_pass_tools_dec, text="📑 Копировать", font=("Arial", 8),
                  command=lambda: self.copy_entry(self.ent_dec_pass)).pack(side="left", expand=True, fill="x", padx=1)
        tk.Button(row_pass_tools_dec, text="❌ Очистить", font=("Arial", 8), bg="#ffebee",
                  command=lambda: self.clear_entry(self.ent_dec_pass)).pack(side="left", expand=True, fill="x", padx=(1,0))

        # 5. Run button
        tk.Button(frame_dec, text="РАСШИФРОВАТЬ", bg="#ccffcc", font=("Arial", 12, "bold"),
                  command=self.on_decrypt_click).pack(side="bottom", fill='x', pady=5)

        self.add_console_widget()
        self.write_log("Готов к работе. Проверьте настройки перед запуском.")

    # --- HELPER METHODS ---

    def select_file(self, entry_widget):
        filename = filedialog.askopenfilename(title="Выберите файл")
        if filename:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filename)

    def select_folder(self, entry_widget):
        folder = filedialog.askdirectory(title="Выберите папку для сохранения")
        if folder:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, folder)

    def toggle_password(self):
        char = "*" if self.is_password_hidden.get() else ""
        self.ent_enc_pass.config(show=char)
        self.ent_dec_pass.config(show=char)


    # --- LOGIC ---

    def on_encrypt_click(self):
        path = self.ent_enc_path.get().strip()
        pwd = self.ent_enc_pass.get().strip()
        
        # Get folder
        out_dir = self.ent_enc_out.get().strip() or None
        
        # Get custom name
        cust_name = self.ent_enc_name.get().strip() or None

        if not path:
            self.write_log("Не выбран файл для шифрования!", is_error=True)
            return
        if not pwd:
            self.write_log("Не введен пароль!", is_error=True)
            return
        
        if not self.app.app_config:
            self.write_log("Конфигурация пуста! Перейдите в настройки.", is_error=True)
            return

        try:
            ext = self.app.app_config.get('general_params', {}).get('extension', '.enc')
            
            output_filename = encrypt_file(
                input_path=path, 
                password=pwd, 
                enc_ext=ext, 
                config=self.app.app_config,
                output_dir=out_dir,
                custom_name=cust_name  
            )
            
            self.write_log(f"Шифрование успешно:\nИсходный: {path}\nПароль: {pwd}\nРезультат: {output_filename}")
        
        except FileExistsError as e:
            self.write_log(f"ОШИБКА ИМЕНИ: {e}", is_error=True)
        except OSError as e:
            self.write_log(f"СИСТЕМНАЯ ОШИБКА: {e}", is_error=True)
        except (MemoryError, OverflowError):
            self.write_log("КРИТИЧЕСКАЯ ОШИБКА: Не хватает оперативной памяти для загрузки файла!", is_error=True)
        except Exception as e:
            self.write_log(f"Ошибка при шифровании: {e}", is_error=True)

    def on_decrypt_click(self):
        path = self.ent_dec_path.get().strip()
        pwd = self.ent_dec_pass.get().strip()
        
        out_dir = self.ent_dec_out.get().strip()
        if not out_dir:
            out_dir = None

        if not path:
            self.write_log("Не выбран файл!", is_error=True)
            return
        if not pwd:
            self.write_log("Не введен пароль!", is_error=True)
            return

        try:
            output_filename = decrypt_file(
                input_path=path, 
                password=pwd,
                config=self.app.app_config,
                output_dir=out_dir 
            )
            self.write_log(f"Расшифровано успешно:\nИсходный файл: {path}\nПароль: {pwd}\nРезультат: {output_filename}")
        except InvalidTag:
            msg = (
                "Ошибка дешифрования (InvalidTag)!\n"
                "Возможные причины:\n"
                "1. Неверный пароль.\n"
                "2. Неверные настройки KDF. Они должны быть такими же, как при шифровании.\n"
                "3. Файл поврежден."
            )
            self.write_log(msg, is_error=True)
        except (MemoryError, OverflowError):
            self.write_log("КРИТИЧЕСКАЯ ОШИБКА: Не хватает памяти для обработки такого Chunk Size.", is_error=True)
        except Exception as e:
            # All other errors (e.g. file not found, no permissions etc.)
            self.write_log(f"Критическая ошибка при дешифровании: {e}", is_error=True)