import tkinter as tk
from tkinter import filedialog
import os

from gui.base_tab import BaseTab

try:
    from core.stego_manager import hide_data_in_image, extract_data_from_image
except ImportError:
    print("Steganography import error")

class StegoTab(BaseTab):
    def setup_ui(self):
        pad_frame = tk.Frame(self.main_frame)
        pad_frame.pack(fill='both', expand=True)
        
        pad_frame.columnconfigure(0, weight=1, uniform="stego")
        pad_frame.columnconfigure(1, weight=1, uniform="stego")

        # === LEFT COLUMN: HIDE ===
        f_hide = tk.LabelFrame(pad_frame, text="Hide file in image", font=("Arial", 11, "bold"), fg="#2980b9", padx=10, pady=10)
        f_hide.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=10)

        # 1. Cover Image
        tk.Label(f_hide, text="Source image:").pack(anchor="w")
        row_cov = tk.Frame(f_hide); row_cov.pack(fill='x', pady=5)
        self.ent_cover = tk.Entry(row_cov); self.ent_cover.pack(side="left", fill="x", expand=True)
        tk.Button(row_cov, text="📂", width=3, command=lambda: self.select_file(self.ent_cover, img=True)).pack(side="right", padx=(5,0))

        # 2. Secret file
        tk.Label(f_hide, text="Data file (what to hide):").pack(anchor="w")
        row_sec = tk.Frame(f_hide); row_sec.pack(fill='x', pady=5)
        self.ent_secret = tk.Entry(row_sec); self.ent_secret.pack(side="left", fill="x", expand=True)
        tk.Button(row_sec, text="📂", width=3, command=lambda: self.select_file(self.ent_secret)).pack(side="right", padx=(5,0))

        # 3. Output filename
        tk.Label(f_hide, text="Output filename (no extension):").pack(anchor="w")
        tk.Label(f_hide, text="(If empty -> ImageName + Suffix)", font=("Arial", 8), fg="gray").pack(anchor="w")
        
        # Create container for field and buttons
        row_name = tk.Frame(f_hide)
        row_name.pack(fill='x', pady=5)
        
        self.ent_out_name = tk.Entry(row_name)
        self.ent_out_name.pack(side="left", fill="x", expand=True)
        
        tk.Button(row_name, text="❌", width=3, 
                  command=lambda: self.clear_entry(self.ent_out_name)).pack(side="right", padx=(2, 0))
        tk.Button(row_name, text="📋", width=3, 
                  command=lambda: self.paste_entry(self.ent_out_name)).pack(side="right", padx=(5, 0))

        # 4. Save folder
        tk.Label(f_hide, text="Save folder:").pack(anchor="w")
        
        row_dir = tk.Frame(f_hide); row_dir.pack(fill='x', pady=(5, 0))
        self.ent_out_dir = tk.Entry(row_dir)
        self.ent_out_dir.pack(side="left", fill="x", expand=True)
        tk.Button(row_dir, text="📂", width=3, command=lambda: self.select_folder(self.ent_out_dir)).pack(side="right", padx=(5,0))

        # --- Radiobuttons for default folder ---
        self.var_default_dir_hide = tk.StringVar(value="cover") # По умолчанию - папка картинки
        
        row_radio = tk.Frame(f_hide)
        row_radio.pack(fill='x', pady=(2, 5))
        
        tk.Label(row_radio, text="If empty, save to:", font=("Arial", 8), fg="gray").pack(side="left")
        
        tk.Radiobutton(row_radio, text="Image folder", variable=self.var_default_dir_hide, 
                       value="cover", font=("Arial", 8)).pack(side="left", padx=5)
        tk.Radiobutton(row_radio, text="File folder", variable=self.var_default_dir_hide, 
                       value="secret", font=("Arial", 8)).pack(side="left")
        # ----------------------------------------------------

        tk.Button(f_hide, text="MERGE", bg="#d6eaf8", font=("Arial", 10, "bold"), 
                  command=self.run_hide).pack(side="bottom", fill='x', pady=20)

        # === RIGHT COLUMN: EXTRACT ===

        f_ext = tk.LabelFrame(pad_frame, text="Извлечь файл из картинки", font=("Arial", 11, "bold"), fg="#27ae60", padx=10, pady=10)
        f_ext.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=10)

        # 1. Stego-file
        tk.Label(f_ext, text="Stego-image:").pack(anchor="w")
        row_stg = tk.Frame(f_ext); row_stg.pack(fill='x', pady=5)
        self.ent_stego = tk.Entry(row_stg); self.ent_stego.pack(side="left", fill="x", expand=True)
        tk.Button(row_stg, text="📂", width=3, command=lambda: self.select_file(self.ent_stego, img=True)).pack(side="right", padx=(5,0))

        # 2. Where to save
        tk.Label(f_ext, text="Where to save extracted files:").pack(anchor="w")
        
        row_out_e = tk.Frame(f_ext); row_out_e.pack(fill='x', pady=(5, 0))
        self.ent_ext_dir = tk.Entry(row_out_e)
        self.ent_ext_dir.pack(side="left", fill="x", expand=True)
        tk.Button(row_out_e, text="📂", width=3, command=lambda: self.select_folder(self.ent_ext_dir)).pack(side="right", padx=(5,0))

        # --- Checkbox to create folder ---
        self.var_create_subfolder = tk.BooleanVar(value=True) # Enabled by default for order
        
        tk.Checkbutton(f_ext, text="Create folder for output data", 
                       variable=self.var_create_subfolder, font=("Arial", 9)).pack(anchor="w", pady=(2, 5))
        
        tk.Label(f_ext, text="(If path empty -> source file folder)", 
                 font=("Arial", 8), fg="gray").pack(anchor="w")
        # ---------------------------------------

        tk.Button(f_ext, text="EXTRACT DATA", bg="#d5f5e3", font=("Arial", 10, "bold"), 
                  command=self.run_extract).pack(side="bottom", fill='x', pady=20)
        
        
        self.add_console_widget()

    # --- METHODS ---

    def select_file(self, w, img=False):
        ft = [("Images", "*.jpg *.png *.jpeg *.bmp"), ("All", "*.*")] if img else [("All", "*.*")]
        f = filedialog.askopenfilename(filetypes=ft)
        if f: w.delete(0, tk.END); w.insert(0, f)

    def select_folder(self, w):
        d = filedialog.askdirectory()
        if d: w.delete(0, tk.END); w.insert(0, d)

    def run_hide(self):
        cover = self.ent_cover.get().strip()
        secret = self.ent_secret.get().strip()
        custom_name = self.ent_out_name.get().strip()
        custom_dir = self.ent_out_dir.get().strip()

        if not (cover and secret):
            self.write_log("Specify source image and secret file!", is_error=True)
            return

        # 1. Output folder logic
        if custom_dir:
            out_dir = custom_dir
        else:
            mode = self.var_default_dir_hide.get()
            if mode == "secret":
                out_dir = os.path.dirname(secret)
            else:
                out_dir = os.path.dirname(cover)

        # 2. Determine filename
        base_name = os.path.basename(cover)
        name_part, ext_part = os.path.splitext(base_name)
        
        if custom_name:
            final_name = custom_name + ext_part
        else:
            suffix = self.app.app_config.get('general_params', {}).get('stego_suffix', '_stego')
            final_name = name_part + suffix + ext_part

        output_path = os.path.join(out_dir, final_name)

        try:
            # Check before writing
            if os.path.exists(output_path):
                self.write_log(f"Error: File already exists!\n{output_path}", is_error=True)
                return

            hide_data_in_image(cover, secret, output_path)
            self.write_log(f"Successfully created: {output_path}")
            
            orig_size = os.path.getsize(cover)
            new_size = os.path.getsize(output_path)
            self.write_log(f"Size: {orig_size/1024:.2f} KB -> {new_size/1024:.2f} KB")
            
        except Exception as e:
            self.write_log(f"Merge error: {e}", is_error=True)
            

    def run_extract(self):
        stego = self.ent_stego.get().strip()
        user_out_dir = self.ent_ext_dir.get().strip()

        if not stego:
            self.write_log("Select file to extract!", is_error=True)
            return

        # 1. Determine base folder
        if user_out_dir:
            target_dir = user_out_dir
        else:
            target_dir = os.path.dirname(stego)

        # 2. Subfolder logic
        if self.var_create_subfolder.get():
            # Create folder name based on filename (without extension) + _extracted
            folder_name = os.path.splitext(os.path.basename(stego))[0] + "_extracted"
            target_dir = os.path.join(target_dir, folder_name)

        try:
            # Core checks existence and creates target_dir if needed
            img_name, sec_name = extract_data_from_image(stego, target_dir)
            
            self.write_log(f"Successfully extracted to folder:\n{target_dir}")
            self.write_log(f"  + {img_name}")
            self.write_log(f"  + {sec_name}")
            
        except FileExistsError as fe:
            self.write_log(f"OVERWRITE ERROR: {fe}\nFiles were not extracted.", is_error=True)
        except ValueError as ve:
            self.write_log(f"Validation error: {ve}", is_error=True)
        except Exception as e:
            self.write_log(f"Extraction error: {e}", is_error=True)