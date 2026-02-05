import tkinter as tk
from tkinter import filedialog
import threading # For background work so UI doesn't freeze during long encryption

from gui.base_tab import BaseTab

# Import
try:
    from core.crypto_manager import build_manifest, restore_from_manifest
    from cryptography.exceptions import InvalidTag
except ImportError:
    print("Core import error in manifest.py")

class ManifestTab(BaseTab):
    def setup_ui(self):
        self.is_password_hidden = tk.BooleanVar(value=False)
        
        pad = tk.Frame(self.main_frame)
        pad.pack(fill='both', expand=True)
        
        # Password Checkbox
        tk.Checkbutton(pad, text="Hide password", variable=self.is_password_hidden, 
                       command=self.toggle_password).pack(anchor="w", pady=(0,10))

        # Column split
        cols = tk.Frame(pad)
        cols.pack(fill='x', pady=(0, 20))
        cols.columnconfigure(0, weight=1, uniform="group1")
        cols.columnconfigure(1, weight=1, uniform="group1")

        # === LEFT COLUMN: CREATE MANIFEST ===
        f_backup = tk.LabelFrame(cols, text="Create storage", font=("Arial", 11, "bold"), fg="blue", padx=10, pady=10)
        f_backup.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # 1. Source folder
        tk.Label(f_backup, text="Source folder (what to encrypt):").pack(anchor="w")
        row_src = tk.Frame(f_backup); row_src.pack(fill='x', pady=(0, 5))
        self.ent_src_dir = tk.Entry(row_src); self.ent_src_dir.pack(side="left", fill="x", expand=True)
        tk.Button(row_src, text="📂", width=3, command=lambda: self.sel_dir(self.ent_src_dir)).pack(side="right", padx=(5, 0))

        # 2. Vault folder (for .enc files)
        tk.Label(f_backup, text="Vault folder (for .enc files):").pack(anchor="w")
        row_vault = tk.Frame(f_backup); row_vault.pack(fill='x', pady=(0, 5))
        self.ent_vault_dir = tk.Entry(row_vault); self.ent_vault_dir.pack(side="left", fill="x", expand=True)
        tk.Button(row_vault, text="📂", width=3, command=lambda: self.sel_dir(self.ent_vault_dir)).pack(side="right", padx=(5, 0))

        # 3. Manifest folder
        tk.Label(f_backup, text="Manifest folder (opt., default /manifest):").pack(anchor="w")
        row_man = tk.Frame(f_backup); row_man.pack(fill='x', pady=(0, 5))
        self.ent_man_dir = tk.Entry(row_man); self.ent_man_dir.pack(side="left", fill="x", expand=True)
        tk.Button(row_man, text="📂", width=3, command=lambda: self.sel_dir(self.ent_man_dir)).pack(side="right", padx=(5, 0))

        # 4. Password
        tk.Label(f_backup, text="Password:").pack(anchor="w")
        self.ent_pass_bak = tk.Entry(f_backup, show="")
        self.ent_pass_bak.pack(fill='x', pady=(0, 5))

        # Buttons
        row_pass_bak = tk.Frame(f_backup)
        row_pass_bak.pack(fill='x', pady=(0, 15))
        tk.Button(row_pass_bak, text="📋 Paste", font=("Arial", 8), bg="#e0f7fa",
                  command=lambda: self.paste_entry(self.ent_pass_bak)).pack(side="left", expand=True, fill="x", padx=(0,1))
        tk.Button(row_pass_bak, text="📑 Copy", font=("Arial", 8),
                  command=lambda: self.copy_entry(self.ent_pass_bak)).pack(side="left", expand=True, fill="x", padx=1)
        tk.Button(row_pass_bak, text="❌ Clear", font=("Arial", 8), bg="#ffebee",
                  command=lambda: self.clear_entry(self.ent_pass_bak)).pack(side="left", expand=True, fill="x", padx=(1,0))

        tk.Button(f_backup, text="CREATE MANIFEST", bg="#ffcccc", font=("Arial", 10, "bold"), 
                  command=self.run_backup).pack(side="bottom", fill='x', pady=5)


        # === RIGHT COLUMN: RESTORE ===
        f_restore = tk.LabelFrame(cols, text="Restore from storage", font=("Arial", 11, "bold"), fg="green", padx=10, pady=10)
        f_restore.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # 1. Manifest FILE (Changed from folder to file)
        tk.Label(f_restore, text="File manifest.json:").pack(anchor="w")
        row_json = tk.Frame(f_restore); row_json.pack(fill='x', pady=(0, 5))
        self.ent_json_path = tk.Entry(row_json); self.ent_json_path.pack(side="left", fill="x", expand=True)
        tk.Button(row_json, text="📂", width=3, command=lambda: self.sel_file(self.ent_json_path)).pack(side="right", padx=(5, 0))

        # 2. Vault folder (where .enc are)
        tk.Label(f_restore, text="Folder with .enc files:").pack(anchor="w")
        row_vault_src = tk.Frame(f_restore); row_vault_src.pack(fill='x', pady=(0, 5))
        self.ent_vault_src = tk.Entry(row_vault_src); self.ent_vault_src.pack(side="left", fill="x", expand=True)
        tk.Button(row_vault_src, text="📂", width=3, command=lambda: self.sel_dir(self.ent_vault_src)).pack(side="right", padx=(5, 0))

        # 3. Where to restore
        tk.Label(f_restore, text="Restore to:").pack(anchor="w")
        row_out = tk.Frame(f_restore); row_out.pack(fill='x', pady=(0, 5))
        self.ent_out_dir = tk.Entry(row_out); self.ent_out_dir.pack(side="left", fill="x", expand=True)
        tk.Button(row_out, text="📂", width=3, command=lambda: self.sel_dir(self.ent_out_dir)).pack(side="right", padx=(5, 0))

        # 4. Password
        tk.Label(f_restore, text="Password:").pack(anchor="w")
        self.ent_pass_res = tk.Entry(f_restore, show="")
        self.ent_pass_res.pack(fill='x', pady=(0, 5))

        # Buttons
        row_pass_res = tk.Frame(f_restore)
        row_pass_res.pack(fill='x', pady=(0, 15))
        tk.Button(row_pass_res, text="📋 Paste", font=("Arial", 8), bg="#e0f7fa",
                  command=lambda: self.paste_entry(self.ent_pass_res)).pack(side="left", expand=True, fill="x", padx=(0,1))
        tk.Button(row_pass_res, text="📑 Copy", font=("Arial", 8),
                  command=lambda: self.copy_entry(self.ent_pass_res)).pack(side="left", expand=True, fill="x", padx=1)
        tk.Button(row_pass_res, text="❌ Clear", font=("Arial", 8), bg="#ffebee",
                  command=lambda: self.clear_entry(self.ent_pass_res)).pack(side="left", expand=True, fill="x", padx=(1,0))

        tk.Button(f_restore, text="RESTORE FILES", bg="#ccffcc", font=("Arial", 10, "bold"), 
                  command=self.run_restore).pack(side="bottom", fill='x', pady=5)

        self.add_console_widget()

    # --- HELPER METHODS ---
    def sel_dir(self, widget):
        d = filedialog.askdirectory()
        if d:
            widget.delete(0, tk.END)
            widget.insert(0, d)
            
    def sel_file(self, widget):
        f = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if f:
            widget.delete(0, tk.END)
            widget.insert(0, f)

    def toggle_password(self):
        char = "*" if self.is_password_hidden.get() else ""
        self.ent_pass_bak.config(show=char)
        self.ent_pass_res.config(show=char)

    # --- LOGIC ---
    def run_backup(self):
        src = self.ent_src_dir.get().strip()
        vault = self.ent_vault_dir.get().strip()
        pwd = self.ent_pass_bak.get().strip()
        
        # Optional manifest folder
        man_dir = self.ent_man_dir.get().strip() or None

        if not (src and vault and pwd):
            self.write_log("Fill main fields left!", is_error=True)
            return
        
        def log_cb(msg, is_error=False):
            self.write_log(msg, is_error)

        def worker():
            try:
                self.write_log("--- START CREATING MANIFEST ---")
                
                # Pass new argument custom_manifest_dir
                actual_man_path = build_manifest(
                    root_dir=src,
                    vault_dir=vault,
                    password=pwd,
                    config=self.app.app_config,
                    status_callback=log_cb,
                    custom_manifest_dir=man_dir
                )
                self.write_log(f"Manifest saved in:\n{actual_man_path}")
                self.write_log("--- DONE ---")
            except Exception as e:
                self.write_log(f"Critical error: {e}", is_error=True)

        threading.Thread(target=worker, daemon=True).start()


    def run_restore(self):
        json_path = self.ent_json_path.get().strip() 
        vault = self.ent_vault_src.get().strip()     
        out = self.ent_out_dir.get().strip()
        pwd = self.ent_pass_res.get().strip()

        if not (json_path and vault and out and pwd):
            self.write_log("Fill all fields right!", is_error=True)
            return
        
        def log_cb(msg, is_error=False):
            self.write_log(msg, is_error)

        def worker():
            try:
                self.write_log("--- START RESTORING ---")
                # Pass json_path and vault separately
                restore_from_manifest(
                    manifest_path=json_path,
                    vault_dir=vault,
                    output_dir=out,
                    password=pwd,
                    config=self.app.app_config,
                    status_callback=log_cb
                )
                self.write_log("--- DONE ---")
            except InvalidTag:
                msg = (
                    "Decryption error (InvalidTag)!\n"
                    "Possible reasons:\n"
                    "1. Invalid password.\n"
                    "2. Incorrect KDF settings. They must be same as during encryption.\n"
                    "3. File corrupted."
                )
                self.write_log(msg, is_error=True)
            except Exception as e:
                self.write_log(f"{e}", is_error=True)

        threading.Thread(target=worker, daemon=True).start()