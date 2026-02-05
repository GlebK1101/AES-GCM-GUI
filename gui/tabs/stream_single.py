import tkinter as tk
from tkinter import filedialog
from cryptography.exceptions import InvalidTag 
from gui.base_tab import BaseTab

try:
    from core.crypto_manager import encrypt_file_stream_single, decrypt_file_stream_single
except ImportError:
    print("Core import error")

class StreamSingleTab(BaseTab):
    def setup_ui(self):
        self.is_password_hidden = tk.BooleanVar(value=False)

        pad_frame = tk.Frame(self.main_frame)
        pad_frame.pack(fill='both', expand=True)

        chk_hide = tk.Checkbutton(pad_frame, text="Hide password", 
                                  variable=self.is_password_hidden, 
                                  command=self.toggle_password)
        chk_hide.pack(anchor="w", pady=(0, 10))

        top_frame = tk.Frame(pad_frame)
        top_frame.pack(fill='x', pady=(0, 20))
        top_frame.columnconfigure(0, weight=1, uniform="grp_s")
        top_frame.columnconfigure(1, weight=1, uniform="grp_s")

        # === LEFT COLUMN: ENCRYPTION (STREAM) ===
        frame_enc = tk.LabelFrame(top_frame, text="Encryption", font=("Arial", 12, "bold"), fg="#8e44ad", padx=10, pady=10)
        frame_enc.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # 1. File
        tk.Label(frame_enc, text="File:").pack(anchor="w")
        f_e1 = tk.Frame(frame_enc); f_e1.pack(fill='x', pady=(0,5))
        self.ent_enc_path = tk.Entry(f_e1); self.ent_enc_path.pack(side="left", fill="x", expand=True)
        tk.Button(f_e1, text="📂", width=3, command=lambda: self.select_file(self.ent_enc_path)).pack(side="right", padx=(5,0))

        # 2. Save folder
        tk.Label(frame_enc, text="Save folder (default near):").pack(anchor="w")
        f_e2 = tk.Frame(frame_enc); f_e2.pack(fill='x', pady=(0,5))
        self.ent_enc_out = tk.Entry(f_e2); self.ent_enc_out.pack(side="left", fill="x", expand=True)
        tk.Button(f_e2, text="📂", width=3, command=lambda: self.select_folder(self.ent_enc_out)).pack(side="right", padx=(5,0))

        # 3. Name
        tk.Label(frame_enc, text="Output filename (opt., no .enc):").pack(anchor="w")
        
        row_name_enc = tk.Frame(frame_enc)
        row_name_enc.pack(fill='x', pady=(0, 5))
        
        self.ent_enc_name = tk.Entry(row_name_enc)
        self.ent_enc_name.pack(side="left", fill="x", expand=True)
        tk.Button(row_name_enc, text="📋", width=3, 
                  command=lambda: self.paste_entry(self.ent_enc_name)).pack(side="right", padx=(5, 0))

        # 4. Password
        tk.Label(frame_enc, text="Password:").pack(anchor="w")
        self.ent_enc_pass = tk.Entry(frame_enc, show="") 
        self.ent_enc_pass.pack(fill='x', pady=(0, 5)) # pady уменьшил, так как снизу кнопки
        
        # Row of password buttons
        row_pass_tools_enc = tk.Frame(frame_enc)
        row_pass_tools_enc.pack(fill='x', pady=(0, 15))
        
        tk.Button(row_pass_tools_enc, text="📋 Paste", font=("Arial", 8), bg="#e0f7fa",
                  command=lambda: self.paste_entry(self.ent_enc_pass)).pack(side="left", expand=True, fill="x", padx=(0,1))
        tk.Button(row_pass_tools_enc, text="📑 Copy", font=("Arial", 8),
                  command=lambda: self.copy_entry(self.ent_enc_pass)).pack(side="left", expand=True, fill="x", padx=1)
        tk.Button(row_pass_tools_enc, text="❌ Clear", font=("Arial", 8), bg="#ffebee",
                  command=lambda: self.clear_entry(self.ent_enc_pass)).pack(side="left", expand=True, fill="x", padx=(1,0))

        tk.Button(frame_enc, text="ENCRYPT", bg="#e8daef", font=("Arial", 12, "bold"), 
                  command=self.on_encrypt_click).pack(side="bottom", fill='x', pady=5)

        # === RIGHT COLUMN: DECRYPTION (STREAM) ===
        frame_dec = tk.LabelFrame(top_frame, text="Decryption", font=("Arial", 12, "bold"), fg="#27ae60", padx=10, pady=10)
        frame_dec.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # 1. File
        tk.Label(frame_dec, text="File (.enc):").pack(anchor="w")
        f_d1 = tk.Frame(frame_dec); f_d1.pack(fill='x', pady=(0,5))
        self.ent_dec_path = tk.Entry(f_d1); self.ent_dec_path.pack(side="left", fill="x", expand=True)
        tk.Button(f_d1, text="📂", width=3, command=lambda: self.select_file(self.ent_dec_path)).pack(side="right", padx=(5,0))

        # 2. Save folder
        tk.Label(frame_dec, text="Save folder (default near):").pack(anchor="w")
        f_d2 = tk.Frame(frame_dec); f_d2.pack(fill='x', pady=(0,5))
        self.ent_dec_out = tk.Entry(f_d2); self.ent_dec_out.pack(side="left", fill="x", expand=True)
        tk.Button(f_d2, text="📂", width=3, command=lambda: self.select_folder(self.ent_dec_out)).pack(side="right", padx=(5,0))

        # Spacer for alignment (empty label and invisible field)
        tk.Label(frame_dec, text=" ").pack(anchor="w")
        tk.Entry(frame_dec, state="disabled", relief="flat", bg=frame_dec.cget("bg")).pack(fill='x', pady=(0,12))

        # 3. Password
        tk.Label(frame_dec, text="Password:").pack(anchor="w")
        self.ent_dec_pass = tk.Entry(frame_dec, show="")
        self.ent_dec_pass.pack(fill='x', pady=(0, 5))

        # Row of password buttons
        row_pass_tools_dec = tk.Frame(frame_dec)
        row_pass_tools_dec.pack(fill='x', pady=(0, 15))
        
        tk.Button(row_pass_tools_dec, text="📋 Paste", font=("Arial", 8), bg="#e0f7fa",
                  command=lambda: self.paste_entry(self.ent_dec_pass)).pack(side="left", expand=True, fill="x", padx=(0,1))
        tk.Button(row_pass_tools_dec, text="📑 Copy", font=("Arial", 8),
                  command=lambda: self.copy_entry(self.ent_dec_pass)).pack(side="left", expand=True, fill="x", padx=1)
        tk.Button(row_pass_tools_dec, text="❌ Clear", font=("Arial", 8), bg="#ffebee",
                  command=lambda: self.clear_entry(self.ent_dec_pass)).pack(side="left", expand=True, fill="x", padx=(1,0))

        tk.Button(frame_dec, text="DECRYPT", bg="#d5f5e3", font=("Arial", 12, "bold"), 
                  command=self.on_decrypt_click).pack(side="bottom", fill='x', pady=5)

        self.add_console_widget()

    # --- METHODS ---

    def toggle_password(self):
        char = "*" if self.is_password_hidden.get() else ""
        self.ent_enc_pass.config(show=char)
        self.ent_dec_pass.config(show=char)

    def select_file(self, w):
        f = filedialog.askopenfilename()
        if f: w.delete(0, tk.END); w.insert(0, f)

    def select_folder(self, w):
        d = filedialog.askdirectory()
        if d: w.delete(0, tk.END); w.insert(0, d)

    def on_encrypt_click(self):
        path = self.ent_enc_path.get().strip()
        pwd = self.ent_enc_pass.get().strip()
        out = self.ent_enc_out.get().strip() or None
        name = self.ent_enc_name.get().strip() or None

        if not path:
            self.write_log("Fill path", is_error=True)
            return
        
        if not pwd:
            self.write_log("Fill password", is_error=True)
            return
        
        try:
            ext = self.app.app_config.get('general_params', {}).get('extension', '.enc')
            res = encrypt_file_stream_single(path, pwd, ext, self.app.app_config, out, name)
            
            self.write_log(f"Stream encryption finished:\nSource: {path}\nPassword: {pwd}\nResult: {res}")
        except FileExistsError as e:
            self.write_log(f"NAME ERROR: {e}", is_error=True)
        except OSError as e:
            # Disk errors (space, access) displayed cleanly
            self.write_log(f"SYSTEM ERROR: {e}", is_error=True)
        except (MemoryError, OverflowError):
            # If RAM ran out
            self.write_log("CRITICAL ERROR: Not enough RAM! Decrease Chunk Size in settings.", is_error=True)
        except Exception as e:
            # Other errors in one line
            self.write_log(e, is_error=True)

    def on_decrypt_click(self):
        path = self.ent_dec_path.get().strip()
        pwd = self.ent_dec_pass.get().strip()
        out = self.ent_dec_out.get().strip() or None

        if not path:
            self.write_log("Fill path", is_error=True)
            return
        
        if not pwd:
            self.write_log("Fill password", is_error=True)
            return

        try:
            res = decrypt_file_stream_single(path, pwd, self.app.app_config, output_dir=out)
            self.write_log(f"Stream decryption finished:\nResult: {res}")
        except InvalidTag:
            # --- HANDLE INVALID PASSWORD ---
            msg = (
                "Decryption error (InvalidTag)!\n"
                "Possible reasons:\n"
                "1. Invalid password.\n"
                "2. Incorrect KDF settings. They must be same as during encryption.\n"
                "3. File corrupted."
            )
            self.write_log(msg, is_error=True)
        except (MemoryError, OverflowError):
            self.write_log("CRITICAL ERROR: Not enough memory to process such Chunk Size.", is_error=True)
        except Exception as e:
            self.write_log(f"Error: {e}", is_error=True)