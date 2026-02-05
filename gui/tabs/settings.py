import tkinter as tk
from tkinter import ttk, filedialog
import json
import pprint

from gui.base_tab import BaseTab

class SettingsTab(BaseTab):
    def setup_ui(self):
        # Container for centering
        center_frame = tk.Frame(self.main_frame)
        center_frame.pack(expand=True)

        # Settings group
        grp_kdf = tk.LabelFrame(center_frame, text="Parameters", 
                                padx=20, pady=20, font=("Arial", 12, "bold"))
        grp_kdf.pack()

        # === CREATE INPUT FIELDS ===
        # We save them in self to access them from other methods (save, import)

        # 1. Min Name Len
        tk.Label(grp_kdf, text="Min Name Len:").grid(row=0, column=0, sticky="e", padx=5, pady=10)
        self.enc_min_len = tk.Entry(grp_kdf, width=15)
        self.enc_min_len.grid(row=0, column=1, padx=5, pady=10)
        self.enc_min_len.insert(0, "16")

        # 2. Max Name Len
        tk.Label(grp_kdf, text="Max Name Len:").grid(row=0, column=2, sticky="e", padx=5, pady=10)
        self.enc_max_len = tk.Entry(grp_kdf, width=15)
        self.enc_max_len.grid(row=0, column=3, padx=5, pady=10)
        self.enc_max_len.insert(0, "32")

        # 3. AAD
        tk.Label(grp_kdf, text="AAD:").grid(row=1, column=0, sticky="e", padx=5, pady=10)
        self.enc_AAD = tk.Entry(grp_kdf, width=15)
        self.enc_AAD.grid(row=1, column=1, padx=5, pady=10)
        self.enc_AAD.insert(0, "None")

        # 4. Chunk Size
        tk.Label(grp_kdf, text="Chunk Size (b):").grid(row=1, column=2, sticky="e", padx=5, pady=10)
        self.enc_CHUNK_SIZE = tk.Entry(grp_kdf, width=15)
        self.enc_CHUNK_SIZE.grid(row=1, column=3, padx=5, pady=10)
        self.enc_CHUNK_SIZE.insert(0, str(64*1024))

        # 5. Extension
        tk.Label(grp_kdf, text="Extension:").grid(row=2, column=0, sticky="e", padx=5, pady=10)
        self.enc_ext = tk.Entry(grp_kdf, width=15)
        self.enc_ext.grid(row=2, column=1, padx=5, pady=10)
        self.enc_ext.insert(0, ".enc")
        
        # 5.1. Stego Suffix
        tk.Label(grp_kdf, text="Stego Suffix:").grid(row=2, column=2, sticky="e", padx=5, pady=10)
        self.ent_stego_suffix = tk.Entry(grp_kdf, width=15)
        self.ent_stego_suffix.grid(row=2, column=3, padx=5, pady=10)
        self.ent_stego_suffix.insert(0, "_stego")

        # Separator
        tk.Label(grp_kdf, text="Argon2id KDF Params", font=("Arial", 10, "italic"), fg="gray")\
            .grid(row=3, column=0, columnspan=4, pady=(15, 5))

        # 6. Key Length (Combobox)
        tk.Label(grp_kdf, text="Key Length:").grid(row=4, column=0, sticky="e", padx=5, pady=10)
        self.ent_length = ttk.Combobox(grp_kdf, values=["16", "24", "32"], width=12, state="readonly")
        self.ent_length.grid(row=4, column=1, padx=5, pady=10)
        self.ent_length.current(2) # 32

        # 7. Iterations
        tk.Label(grp_kdf, text="Iterations:").grid(row=4, column=2, sticky="e", padx=5, pady=10)
        self.ent_iterations = tk.Entry(grp_kdf, width=15)
        self.ent_iterations.grid(row=4, column=3, padx=5, pady=10)
        self.ent_iterations.insert(0, "3")

        # 8. Memory Cost
        tk.Label(grp_kdf, text="Memory (KiB):").grid(row=5, column=0, sticky="e", padx=5, pady=10)
        self.ent_memory = tk.Entry(grp_kdf, width=15)
        self.ent_memory.grid(row=5, column=1, padx=5, pady=10)
        self.ent_memory.insert(0, str(64 * 1024))

        # 9. Lanes
        tk.Label(grp_kdf, text="Lanes:").grid(row=5, column=2, sticky="e", padx=5, pady=10)
        self.ent_lanes = tk.Entry(grp_kdf, width=15)
        self.ent_lanes.grid(row=5, column=3, padx=5, pady=10)
        self.ent_lanes.insert(0, "1")

        # === BUTTONS ===
        
        btn_save = tk.Button(grp_kdf, text="Apply settings", bg="#ddd", command=self.save_settings)
        btn_save.grid(row=6, column=0, columnspan=4, pady=(10, 0), sticky="we") 

        btn_export = tk.Button(grp_kdf, text="Export JSON",  bg="#ddd", command=self.export_config)
        btn_export.grid(row=7, column=0, columnspan=2, pady=(10, 0), sticky="we") 

        btn_import = tk.Button(grp_kdf, text="Import JSON",  bg="#ddd", command=self.import_config)
        btn_import.grid(row=7, column=2, columnspan=2, pady=(10, 0), sticky="we")

        self.add_console_widget()

    # === LOGIC ===

    def _calc_val(self, val_str):
        """Internal method to evaluate expressions (e.g. 64*1024)"""
        if not val_str.strip():
            raise ValueError("Numeric field cannot be empty")
        try:
            return int(eval(val_str, {"__builtins__": None}, {}))
        except Exception:
            raise ValueError(f"Failed to calculate value: {val_str}")

    def save_settings(self):
        try:
            # 1. First read and calc name lengths
            val_min_len = self._calc_val(self.enc_min_len.get())
            val_max_len = self._calc_val(self.enc_max_len.get())

            # 2. LOGIC CHECK
            if val_min_len > val_max_len:
                raise ValueError(
                    f"Logic error: Min Name Len ({val_min_len}) "
                    f"cannot be greater than Max Name Len ({val_max_len})!"
                )
            
            # 3. Extension check
            if not self.enc_ext.get().strip():
                raise ValueError("Field 'Extension' cannot be empty")
            
            # 4. AAD Processing
            raw_aad = self.enc_AAD.get().strip()
            final_aad = None if (raw_aad == "None" or raw_aad == "") else raw_aad

            # 5. Form config
            new_config = {
                "filename_params": {
                    "min_len": val_min_len,
                    "max_len": val_max_len
                },
                "streaming_params": {
                    "chunk_size": self._calc_val(self.enc_CHUNK_SIZE.get())
                },
                "general_params": {
                    "aad": final_aad,
                    "extension": self.enc_ext.get().strip(),
                    "stego_suffix": self.ent_stego_suffix.get().strip() or "_stego"
                },
                "kdf_params": {
                    "length": self._calc_val(self.ent_length.get()),
                    "iterations": self._calc_val(self.ent_iterations.get()),
                    "memory_cost": self._calc_val(self.ent_memory.get()), 
                    "lanes": self._calc_val(self.ent_lanes.get())
                }
            }
            
            # --- UPDATE GLOBAL CONFIG ---
            self.app.app_config.clear()
            self.app.app_config.update(new_config)
            
            # Log
            formatted = pprint.pformat(self.app.app_config, indent=4)
            self.write_log(f"Configuration applied:\n{formatted}")
            
        except ValueError as e:
            self.write_log(f"Data validation error:\n{e}", is_error=True)

    def export_config(self):
        if not self.app.app_config:
            self.write_log("Configuration is empty. Click 'Apply' first.", is_error=True)
            return
            
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.app.app_config, f, indent=4)
                self.write_log(f"Saved to file:\n{filename}")
            except Exception as e:
                self.write_log(f"Error saving: {e}", is_error=True)

    def import_config(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Fill GUI fields with data from file
                self.enc_min_len.delete(0, tk.END); self.enc_min_len.insert(0, data['filename_params']['min_len'])
                self.enc_max_len.delete(0, tk.END); self.enc_max_len.insert(0, data['filename_params']['max_len'])
                self.enc_CHUNK_SIZE.delete(0, tk.END); self.enc_CHUNK_SIZE.insert(0, data['streaming_params']['chunk_size'])
                self.enc_ext.delete(0, tk.END); self.enc_ext.insert(0, data['general_params']['extension'])
                
                aad_val = data['general_params']['aad']
                self.enc_AAD.delete(0, tk.END)
                self.enc_AAD.insert(0, "None" if aad_val is None else aad_val)
                
                suffix = data['general_params'].get('stego_suffix', '_stego')
                self.ent_stego_suffix.delete(0, tk.END)
                self.ent_stego_suffix.insert(0, suffix)
                
                self.ent_length.set(data['kdf_params']['length']) 
                self.ent_iterations.delete(0, tk.END); self.ent_iterations.insert(0, data['kdf_params']['iterations'])
                self.ent_memory.delete(0, tk.END); self.ent_memory.insert(0, data['kdf_params']['memory_cost'])
                self.ent_lanes.delete(0, tk.END); self.ent_lanes.insert(0, data['kdf_params']['lanes'])
                
                # Apply (update app_config dict)
                self.save_settings()
                self.write_log(f"Configuration loaded from file:\n{filename}")
                
            except Exception as e:
                self.write_log(f"Import error: {e}", is_error=True)