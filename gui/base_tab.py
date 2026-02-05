import tkinter as tk
from tkinter import ttk, messagebox
import datetime

class BaseTab(ttk.Frame):
    def __init__(self, parent, app_context):
        super().__init__(parent)
        self.app = app_context 
        self.console_widget = None 
        
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.setup_ui()

    def setup_ui(self):
        pass

    def add_console_widget(self):
        self.console_widget = tk.Text(self, height=16, bg="#f0f0f0", state='disabled')
        self.console_widget.pack(fill='x', padx=10, pady=(0, 10), side='bottom')
        
        ctrl_frame = tk.Frame(self)
        ctrl_frame.pack(fill='x', padx=10, pady=(0, 5), side='bottom')
        
        tk.Button(ctrl_frame, text="Copy", font=("Arial", 8), 
                 command=self.copy_console).pack(side="right")
        
        tk.Button(ctrl_frame, text="Clear", font=("Arial", 8), 
                 command=self.clear_console).pack(side="right", padx=5)

        tk.Label(ctrl_frame, text="Operation log:", font=("Arial", 9, "bold")).pack(side="left")

    def write_log(self, message, is_error=False):
        if not self.console_widget:
            return

        def _update_ui():
            # current_time = datetime.datetime.now().strftime("%H:%M:%S")
            prefix = "❌ " if is_error else ""
            
            full_message = f"{prefix}{message}\n"
            separator = "-" * 80 + "\n"
            
            self.console_widget.config(state='normal')
            self.console_widget.insert(tk.END, full_message + separator)
            self.console_widget.see(tk.END)
            self.console_widget.config(state='disabled')

        self.after(0, _update_ui)

    def clear_console(self):
        if self.console_widget:
            self.console_widget.config(state='normal')
            self.console_widget.delete("1.0", tk.END)
            self.console_widget.config(state='disabled')

    def copy_console(self):
        if self.console_widget:
            try:
                text = self.console_widget.get("1.0", "end-1c")
                self.clipboard_clear()
                self.clipboard_append(text)
                self.update()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy: {e}")
    
    # --- METHODS ---
    
    def paste_entry(self, entry_widget):
        try:
            text = self.clipboard_get()
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, text)
        except tk.TclError:
            pass 

    def clear_entry(self, entry_widget):
        entry_widget.delete(0, tk.END)

    def copy_entry(self, entry_widget):
        try:
            text = entry_widget.get()
            if text:
                self.clipboard_clear()
                self.clipboard_append(text)
                self.update() 
        except tk.TclError:
            pass