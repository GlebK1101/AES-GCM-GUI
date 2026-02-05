import tkinter as tk
from tkinter import ttk

from gui.base_tab import BaseTab
from gui.tabs.settings import SettingsTab
from gui.tabs.manifest import ManifestTab
from gui.tabs.encryption import EncryptionTab 
from gui.tabs.about import AboutTab
from gui.tabs.stream_single import StreamSingleTab
from gui.tabs.utilities import UtilitiesTab
from gui.tabs.shredder import ShredderTab
from gui.tabs.stego import StegoTab

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Argon2id & AES-GCM Encryptor")
        self.geometry("800x800")

        # Default configuration
        self.app_config = {
            'filename_params': {'max_len': 32, 'min_len': 16},
            'general_params': {'aad': None, 'extension': '.enc'},
            'kdf_params': {'iterations': 3, 'lanes': 1, 'length': 32, 'memory_cost': 65536},
            'streaming_params': {'chunk_size': 65536}
        }

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')

        # --- TAB INITIALIZATION ---
        
        # Одиночный файл / Single file
        self.tab_encryption = EncryptionTab(self.notebook, self)
        self.notebook.add(self.tab_encryption, text='Одиночный файл')
        # Поток / Stream
        self.tab_stream = StreamSingleTab(self.notebook, self)
        self.notebook.add(self.tab_stream, text='Поток')
        # Манифест / Manifest
        self.tab_manifest = ManifestTab(self.notebook, self)
        self.notebook.add(self.tab_manifest, text='Манифест')
        # Стеганография / Steganography
        self.tab_stego = StegoTab(self.notebook, self)
        self.notebook.add(self.tab_stego, text='Стеганография')
        # Шредер / Shredder
        self.tab_shredder = ShredderTab(self.notebook, self)
        self.notebook.add(self.tab_shredder, text='Шредер')
        # Настройки / Settings
        self.tab_settings = SettingsTab(self.notebook, self)
        self.notebook.add(self.tab_settings, text='Настройки')
        # Утилиты / Utilities
        self.tab_utils = UtilitiesTab(self.notebook, self)
        self.notebook.add(self.tab_utils, text='Утилиты')
        # О программе / About
        self.tab_about = AboutTab(self.notebook, self)
        self.notebook.add(self.tab_about, text='О программе')    