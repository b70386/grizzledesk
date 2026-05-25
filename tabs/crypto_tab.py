# tabs/crypto_tab.py
import customtkinter as ctk
import threading
from datetime import datetime

class CryptoTab:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app  # Referensi ke instance utama GrizzleDesk
        self.setup_ui()
        
    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header text
        ctk.CTkLabel(self.main_frame, text="Crypto Monitoring", font=("Arial", 24, "bold")).pack(pady=10)
        ctk.CTkLabel(self.main_frame, text="Real-time Crypto Prices via Binance & Market API", font=("Arial", 14), text_color="green").pack(pady=(0, 20))
        
        # Container untuk kartu-kartu koin (Grid Layout)
        self.cards_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=10, pady=10)
        
        # --- KARTU BITCOIN (BTC) ---
        self.btc_card = ctk.CTkFrame(self.cards_frame, corner_radius=10, border_width=2, border_color="#d48a00")
        self.btc_card.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(self.btc_card, text="🪙 Bitcoin (BTC)", font=("Arial", 20, "bold"), text_color="#d48a00").pack(pady=(15, 5))
        
        self.btc_usd_label = ctk.CTkLabel(self.btc_card, text="$ --,--", font=("Arial", 24, "bold"))
        self.btc_usd_label.pack(pady=5)
        
        self.btc_idr_label = ctk.CTkLabel(self.btc_card, text="Rp --,--", font=("Arial", 18, "bold"), text_color="gray")
        self.btc_idr_label.pack(pady=(0, 15))
        
        # --- KARTU PINETWORK (PI) ---
        self.pi_card = ctk.CTkFrame(self.cards_frame, corner_radius=10, border_width=2, border_color="#d60a50")
        self.pi_card.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(self.pi_card, text="🪙 PiNetwork (PI)", font=("Arial", 20, "bold"), text_color="#d60a50").pack(pady=(15, 5))
        
        self.pi_usd_label = ctk.CTkLabel(self.pi_card, text="$ --,--", font=("Arial", 24, "bold"))
        self.pi_usd_label.pack(pady=5)
        
        self.pi_idr_label = ctk.CTkLabel(self.pi_card, text="Rp --,--", font=("Arial", 18, "bold"), text_color="gray")
        self.pi_idr_label.pack(pady=(0, 15))
        
        # --- KARTU ETHEREUM (ETH) ---
        self.eth_card = ctk.CTkFrame(self.cards_frame, corner_radius=10, border_width=2, border_color="#627eea")
        self.eth_card.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(self.eth_card, text="⟠ Ethereum (ETH)", font=("Arial", 20, "bold"), text_color="#627eea").pack(pady=(15, 5))
        
        self.eth_usd_label = ctk.CTkLabel(self.eth_card, text="$ --,--", font=("Arial", 24, "bold"))
        self.eth_usd_label.pack(pady=5)
        
        self.eth_idr_label = ctk.CTkLabel(self.eth_card, text="Rp --,--", font=("Arial", 18, "bold"), text_color="gray")
        self.eth_idr_label.pack(pady=(0, 15))
        
        # Label Status Pembaruan Waktu
        self.updated_label = ctk.CTkLabel(self.main_frame, text="📅 Waiting for initial fetch...", font=("Arial", 14, "italic"))
        self.updated_label.pack(pady=20)
        
        # Tombol Refresh Manual
        self.refresh_btn = ctk.CTkButton(
            self.main_frame, 
            text="⟳ Refresh Crypto", 
            command=self.trigger_manual_refresh, 
            width=180, 
            height=35,
            font=("Arial", 14, "bold")
        )
        self.refresh_btn.pack(pady=10)

    def trigger_manual_refresh(self):
        """Mematikan interaksi tombol sementara dan memicu refresh instan via thread utama"""
        self.refresh_btn.configure(state="disabled", text="🔄 Refreshing...")
        threading.Thread(target=self._manual_refresh_worker, daemon=True).start()
        
    def _manual_refresh_worker(self):
        self.main_app.fetch_crypto_rates_instantly()
        
    def update_display(self, btc_usd, btc_idr, eth_usd, eth_idr, pi_usd, pi_idr, last_updated_time):
        """Fungsi eksternal yang dipanggil oleh main.py untuk memperbarui teks label di GUI"""
        btc_u_str = f"${btc_usd:,.2f}" if btc_usd else "$ --,--"
        btc_i_str = f"Rp {btc_idr:,.0f}".replace(",", ".") if btc_idr else "Rp --,--"
        eth_u_str = f"${eth_usd:,.2f}" if eth_usd else "$ --,--"
        eth_i_str = f"Rp {eth_idr:,.0f}".replace(",", ".") if eth_idr else "Rp --,--"
        
        # Perbaikan syntax variabel pi dan pembersihan bug typo tanda koma
        pi_u_str = f"${pi_usd:,.2f}" if pi_usd else "$ 0.00 (Mainnet Closed)"
        pi_i_str = f"Rp {pi_idr:,.0f}".replace(",", ".") if pi_idr else "Rp 0 (Mainnet Closed)"
        
        # Update komponen teks label secara aman
        self.btc_usd_label.configure(text=btc_u_str)
        self.btc_idr_label.configure(text=btc_i_str)
        self.eth_usd_label.configure(text=eth_u_str)
        self.eth_idr_label.configure(text=eth_i_str)
        self.pi_usd_label.configure(text=pi_u_str)
        self.pi_idr_label.configure(text=pi_i_str)
        
        time_str = last_updated_time.strftime("%H:%M:%S")
        self.updated_label.configure(text=f"✅ Crypto Updated: {time_str}")
        self.refresh_btn.configure(state="normal", text="⟳ Refresh Crypto")