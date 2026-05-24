# main.py - GrizzleDesk Ultimate Desktop Utility
import customtkinter as ctk
import sys
import os
import threading
import pystray
from PIL import Image

# Set path agar bisa import module dari folder tabs dan utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from tabs.home_tab import HomeTab
    from tabs.notes_tab import NotesTab
    from tabs.currency_tab import CurrencyTab
    from tabs.calculator_tab import CalculatorTab
    from tabs.converter_tab import ConverterTab
    from tabs.onlinetools_tab import OnlineToolsTab
except ImportError as e:
    print(f"Error importing tabs: {e}")
    print("Make sure the 'tabs' folder exists and contains all tab files.")
    input("Press Enter to exit...")
    sys.exit(1)

# Settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class GrizzleDesk(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set unique App User Model ID untuk taskbar Windows
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("GrizzleDesk.Application.1.0")
        except:
            pass
        
        self.title("GrizzleDesk - Ultimate Desktop Utility")
        self.geometry("1000x750")
        self.minsize(900, 650)
        
        # Set icon untuk window dan taskbar (menggunakan resource_path)
        try:
            icon_path = resource_path(os.path.join("assets", "icon.ico"))
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
                self.wm_iconbitmap(icon_path)
                self.after(100, lambda: self.iconbitmap(icon_path))
                print(f"✅ Icon loaded: {icon_path}")
            else:
                print(f"⚠️ Icon not found: {icon_path}")
        except Exception as e:
            print(f"⚠️ Failed to set icon: {e}")
        
        # Tabview (Tab Manager)
        self.tabview = ctk.CTkTabview(self, width=950, height=680)
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Add tabs
        self.tabview.add("🏠 Home")
        self.tabview.add("📝 Notes")
        self.tabview.add("💱 Currency")
        self.tabview.add("🧮 Calculator")
        self.tabview.add("📏 Converter")
        self.tabview.add("🌐 Online Tools")
        
        # Initialize tabs
        self.home_tab = HomeTab(self.tabview.tab("🏠 Home"))
        self.notes_tab = NotesTab(self.tabview.tab("📝 Notes"))
        self.currency_tab = CurrencyTab(self.tabview.tab("💱 Currency"))
        self.calculator_tab = CalculatorTab(self.tabview.tab("🧮 Calculator"))
        self.converter_tab = ConverterTab(self.tabview.tab("📏 Converter"))
        self.onlinetools_tab = OnlineToolsTab(self.tabview.tab("🌐 Online Tools"))
        
        # Status bar (menggunakan Frame agar bisa menampung switch)
        self.status_frame = ctk.CTkFrame(self, height=30, corner_radius=5)
        self.status_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 10))
        self.status_frame.pack_propagate(False)  # Keep height fixed
        
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="✅ Ready | GrizzleDesk v1.0 | 7 Tools Available", 
            anchor="w",
            fg_color="transparent",
        )
        self.status_label.pack(side="left", padx=10, fill="x", expand=True)
        
        # Dark mode toggle switch di status bar (kanan)
        self.theme_switch = ctk.CTkSwitch(
            master=self.status_frame,
            text="🌙 Dark",
            command=self.toggle_theme,
            width=40
        )
        self.theme_switch.pack(side="right", padx=10)
        
        # Tombol Hide to Tray di status bar
        self.hide_tray_btn = ctk.CTkButton(
            master=self.status_frame,
            text="Hide to Tray",
            command=self.hide_to_tray,
            width=100,
            height=25,
            font=("Arial", 12, "bold")
        )
        self.hide_tray_btn.pack(side="right", padx=5)
        
        # === TAMBAHAN: System Tray Setup ===
        self.tray_icon = None
        self.setup_system_tray()
        
        # Override tombol close (X) - Tetap exit, tapi siapkan opsi hide ke tray
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def toggle_theme(self):
        """Toggle between light and dark mode"""
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
            self.theme_switch.configure(text="☀️ Light")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_switch.configure(text="🌙 Dark")
    
    def setup_system_tray(self):
        """Setup system tray icon dengan menu"""
        try:
            # Load icon untuk tray
            icon_path = resource_path(os.path.join("assets", "icon.ico"))
            if os.path.exists(icon_path):
                image = Image.open(icon_path)
                image = image.resize((64, 64))
            else:
                # Fallback: buat icon sederhana
                image = Image.new('RGB', (64, 64), (30, 144, 255))
            
            # Menu tray
            menu = pystray.Menu(
                pystray.MenuItem("Show GrizzleDesk", self.show_window, default=True),
                pystray.MenuItem("Hide to Tray", self.hide_to_tray),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Dark/Light Mode", self.toggle_theme_tray),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit", self.quit_app)
            )
            
            self.tray_icon = pystray.Icon("grizzledesk", image, "GrizzleDesk", menu)
            
            # Jalankan tray di thread terpisah
            self.tray_thread = threading.Thread(target=self._run_tray, daemon=True)
            self.tray_thread.start()
            
        except Exception as e:
            print(f"System tray setup failed: {e}")
    
    def _run_tray(self):
        """Jalankan tray icon dengan event loop sendiri"""
        if self.tray_icon:
            self.tray_icon.run()
    
    def show_window(self, icon=None, item=None):
        """Tampilkan window dari tray"""
        self.after(0, self._show_window_impl)
    
    def _show_window_impl(self):
        self.deiconify()
        self.lift()
        self.focus_force()
        self.attributes('-topmost', True)
        self.after(100, lambda: self.attributes('-topmost', False))
        self.state('normal')
    
    def hide_to_tray(self, icon=None, item=None):
        """Sembunyikan window ke system tray"""
        self.withdraw()
    
    def toggle_theme_tray(self, icon=None, item=None):
        """Toggle theme dari menu tray"""
        current = ctk.get_appearance_mode()
        new_mode = "light" if current == "Dark" else "dark"
        self.after(0, lambda: ctk.set_appearance_mode(new_mode))
        if new_mode == "light":
            self.after(0, lambda: self.theme_switch.configure(text="☀️ Light"))
        else:
            self.after(0, lambda: self.theme_switch.configure(text="🌙 Dark"))
    
    def on_closing(self):
        """Tombol close (X) - exit aplikasi, tidak hide ke tray"""
        self.quit_app()
    
    def quit_app(self, icon=None, item=None):
        """Keluar dari aplikasi sepenuhnya"""
        if self.tray_icon:
            self.tray_icon.stop()
            self.after(100, self.destroy)
        else:
                self.destroy()

if __name__ == "__main__":
    app = GrizzleDesk()
    app.mainloop()