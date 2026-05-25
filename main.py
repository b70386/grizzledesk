# main.py - GrizzleDesk Ultimate Desktop Utility
import customtkinter as ctk
import sys
import os
import threading
import pystray
import time
import requests
from datetime import datetime
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
    from tabs.crypto_tab import CryptoTab  # Import modul tab Crypto Baru
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
        
        # Inisialisasi variabel pelacak kurs fiat
        self.usd_to_idr_rate = "Fetching..."
        self.usd_idr_raw_rate = 16000.0  # Default fallback rate desimal untuk kalkulasi Crypto
        self.is_fetching_rates = False
        self.rate_thread = None
        
        # Inisialisasi variabel pelacak kripto v1.1
        self.is_fetching_crypto = False
        self.crypto_thread = None
        self.btc_usd_value = None
        self.btc_idr_value = None
        self.eth_usd_value = None
        self.eth_idr_value = None
        self.pi_usd_value = None
        self.pi_idr_value = None
        
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
        
        # Add tabs (Termasuk Tab Crypto Monitoring Baru)
        self.tabview.add("🏠 Home")
        self.tabview.add("📝 Notes")
        self.tabview.add("💱 Currency")
        self.tabview.add("🪙 Crypto")  # Penambahan Tab Baru di Menu V1.1
        self.tabview.add("🧮 Calculator")
        self.tabview.add("📏 Converter")
        self.tabview.add("🌐 Online Tools")
        
        # Initialize tabs
        self.home_tab = HomeTab(self.tabview.tab("🏠 Home"))
        self.notes_tab = NotesTab(self.tabview.tab("📝 Notes"))
        self.currency_tab = CurrencyTab(self.tabview.tab("💱 Currency"))
        self.crypto_tab = CryptoTab(self.tabview.tab("🪙 Crypto"), self)  # Oper reference self aplikasi utama
        self.calculator_tab = CalculatorTab(self.tabview.tab("🧮 Calculator"))
        self.converter_tab = ConverterTab(self.tabview.tab("📏 Converter"))
        self.onlinetools_tab = OnlineToolsTab(self.tabview.tab("🌐 Online Tools"))
        
        # Status bar (menggunakan Frame agar bisa menampung switch)
        self.status_frame = ctk.CTkFrame(self, height=30, corner_radius=5)
        self.status_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 10))
        self.status_frame.pack_propagate(False)  # Keep height fixed
        
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="✅ Ready | GrizzleDesk v1.1 Latest | 8 Tools Available", 
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
        
        # === System Tray Setup ===
        self.tray_icon = None
        self.setup_system_tray()
        
        # Override tombol close (X) - Tetap exit, tapi siapkan opsi hide ke tray
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Jalankan background fetcher untuk kurs fiat USD ke IDR (Open ER-API)
        self.start_rate_fetcher()
        
        # Jeda 2 detik sebelum menjalankan background crypto fetcher pertama kali agar data fiat siap
        self.after(2000, self.start_crypto_fetcher)
    
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
            
            # Inisialisasi awal tray title dengan penunjuk kurs default
            initial_title = f"GrizzleDesk\nUSD to IDR: {self.usd_to_idr_rate}"
            self.tray_icon = pystray.Icon("grizzledesk", image, initial_title, menu)
            
            # Jalankan tray di thread terpisah
            self.tray_thread = threading.Thread(target=self._run_tray, daemon=True)
            self.tray_thread.start()
            
        except Exception as e:
            print(f"System tray setup failed: {e}")
    
    def _run_tray(self):
        """Jalankan tray icon dengan event loop sendiri"""
        if self.tray_icon:
            self.tray_icon.run()
    
    def start_rate_fetcher(self):
        """Memulai loop penarikan data kurs di background thread"""
        self.is_fetching_rates = True
        self.rate_thread = threading.Thread(target=self._fetch_rate_loop, daemon=True)
        self.rate_thread.start()
        
    def _fetch_rate_loop(self):
        """Loop pencarian data menggunakan Open ER-API (Update tiap 5 menit)"""
        url = "https://open.er-api.com/v6/latest/USD"
        while self.is_fetching_rates:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, dict):
                        usd_to_idr = data.get("rates", {}).get("IDR")
                        
                        if usd_to_idr:
                            self.usd_idr_raw_rate = float(usd_to_idr)
                            self.usd_to_idr_rate = f"Rp{usd_to_idr:,.2f}"
                            
                            if self.tray_icon:
                                self.tray_icon.title = f"GrizzleDesk\nUSD to IDR: {self.usd_to_idr_rate}"
            except Exception as e:
                print(f"Gagal memperbarui kurs: {e}")
            
            time.sleep(300)

    def start_crypto_fetcher(self):
        """Memulai loop penarikan data harga crypto di background thread v1.1"""
        self.is_fetching_crypto = True
        self.crypto_thread = threading.Thread(target=self._fetch_crypto_loop, daemon=True)
        self.crypto_thread.start()

    def _fetch_crypto_loop(self):
        """Loop pencarian harga Crypto dari Binance API (Otomatis Update tiap 15 menit)"""
        while self.is_fetching_crypto:
            self.fetch_crypto_rates_instantly()
            time.sleep(900)

    def fetch_crypto_rates_instantly(self):
        """Fungsi eksekusi penarikan data kripto instan secara independen"""
        current_fiat_rate = getattr(self, "usd_idr_raw_rate", 16000.0)
        
        # 1. Fetch Bitcoin (Binance)
        try:
            btc_res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=10)
            if btc_res.status_code == 200:
                self.btc_usd_value = float(btc_res.json().get("price", 0))
                self.btc_idr_value = self.btc_usd_value * current_fiat_rate
        except Exception as e:
            print(f"Gagal fetch BTC: {e}")

        # 2. Fetch Ethereum (Binance)
        try:
            eth_res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT", timeout=10)
            if eth_res.status_code == 200:
                self.eth_usd_value = float(eth_res.json().get("price", 0))
                self.eth_idr_value = self.eth_usd_value * current_fiat_rate
        except Exception as e:
            print(f"Gagal fetch ETH: {e}")

        # 3. Fetch Pi Network IOU (Menggunakan API Publik Lain karena Binance tidak ada PIUSDT)
        try:
            # Menggunakan API publik alternatif untuk mengambil data Pi Network IOU market price
            pi_res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=pi-network&vs_currencies=usd", timeout=10)
            if pi_res.status_code == 200:
                self.pi_usd_value = float(pi_res.json().get("pi-network", {}).get("usd", 0))
                self.pi_idr_value = self.pi_usd_value * current_fiat_rate
            else:
                # Fallback internal token dummy jika network rate-limiting aktif
                self.pi_usd_value = 0.0
                self.pi_idr_value = 0.0
        except Exception as e:
            print(f"Gagal fetch PI: {e}")
            self.pi_usd_value = 0.0
            self.pi_idr_value = 0.0

        # Kirim data ke komponen UI CryptoTab
        now = datetime.now()
        self.after(0, lambda: self.crypto_tab.update_display(
            self.btc_usd_value, self.btc_idr_value, 
            self.eth_usd_value, self.eth_idr_value,
            self.pi_usd_value, self.pi_idr_value, now
        ))

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
        """Tombol close (X) - exit aplikasi sepenuhnya"""
        self.quit_app()
    
    def quit_app(self, icon=None, item=None):
        """Keluar dari aplikasi sepenuhnya"""
        self.is_fetching_rates = False 
        self.is_fetching_crypto = False  
        if self.tray_icon:
            self.tray_icon.stop()
            self.after(100, self.destroy)
        else:
            self.destroy()

if __name__ == "__main__":
    app = GrizzleDesk()
    app.mainloop()