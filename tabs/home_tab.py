# tabs/home_tab.py
import customtkinter as ctk
from PIL import Image, ImageDraw
import os
import requests
import json
from datetime import datetime, timedelta

class HomeTab:
    def __init__(self, parent):
        self.parent = parent
        self.usd_idr_rate = None
        self.last_updated = None
        self.cache_file = "usd_idr_cache.json"
        
        self.load_cached_rate()
        self.setup_ui()
        self.fetch_usd_idr_rate()
    
    def load_cached_rate(self):
        """Load cached USD/IDR rate"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    cache = json.load(f)
                    self.usd_idr_rate = cache.get("rate")
                    updated_str = cache.get("last_updated", "")
                    if updated_str:
                        self.last_updated = datetime.fromisoformat(updated_str)
                        if datetime.now() - self.last_updated < timedelta(hours=1):
                            return True
            except:
                pass
        return False
    
    def save_cache(self):
        """Save USD/IDR rate to cache"""
        if self.usd_idr_rate and self.last_updated:
            cache = {
                "rate": self.usd_idr_rate,
                "last_updated": self.last_updated.isoformat()
            }
            with open(self.cache_file, "w") as f:
                json.dump(cache, f)
    
    def fetch_usd_idr_rate(self):
        """Fetch USD to IDR exchange rate menggunakan Open ER-API"""
        try:
            url = "https://open.er-api.com/v6/latest/USD"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and data.get("result") == "success":
                    # Mengambil nilai kurs IDR langsung dari nested object 'rates'
                    rate = data.get("rates", {}).get("IDR")
                    if rate:
                        self.usd_idr_rate = float(rate)
                        self.last_updated = datetime.now()
                        self.save_cache()
                        self.update_rate_display()
                        return
        except Exception as e:
            print(f"Failed to fetch USD/IDR: {e}")
        
        if self.usd_idr_rate:
            self.update_rate_display()
        else:
            self.rate_label.configure(text="1 USD = IDR (offline)", text_color="red")
    
    def update_rate_display(self):
        """Update the rate label with current rate"""
        if self.usd_idr_rate:
            formatted_rate = f"Rp {self.usd_idr_rate:,.0f}".replace(",", ".")
            self.rate_label.configure(
                text=f"1 USD = {formatted_rate}",
                text_color="#d48a00"
            )
            if self.last_updated:
                # Format: Hari, Tanggal Bulan Tahun - Jam:Menit:Detik
                # Contoh: Friday, 23 May 2026 - 18:39:52
                day_name = self.last_updated.strftime("%A")
                date_str = self.last_updated.strftime("%d %B %Y")
                time_str = self.last_updated.strftime("%H:%M:%S")
                self.rate_time_label.configure(text=f" {day_name}, {date_str} - {time_str}")
    
    def load_image_with_round_corners(self, path, size=(350, 180), radius=20):
        """Load image and add rounded corners"""
        if os.path.exists(path):
            try:
                img = Image.open(path).convert("RGBA")
                img = img.resize(size, Image.LANCZOS)
                
                mask = Image.new('L', size, 0)
                draw = ImageDraw.Draw(mask)
                draw.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
                
                result = Image.new('RGBA', size, (0, 0, 0, 0))
                result.paste(img, (0, 0), mask)
                
                return ctk.CTkImage(light_image=result, dark_image=result, size=size)
            except Exception as e:
                print(f"Error loading image: {e}")
        return None
    
    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=5)
     
        # ========== WELCOME TEXT ==========
        ctk.CTkLabel(
            self.main_frame, 
            text="Welcome to GrizzleDesk", 
            font=("Arial", 24, "bold")
        ).pack(pady=(2, 0))
        
        ctk.CTkLabel(
            self.main_frame, 
            text="Ultimate Desktop Utility - All Tools in One Place", 
            font=("Arial", 14),
            text_color="gray"
        ).pack(pady=(0, 5))
        
        # ========== KURS HARI INI ==========
        rate_container = ctk.CTkFrame(self.main_frame, corner_radius=8)
        rate_container.pack(pady=3, padx=30, fill="x")
        
        self.rate_label = ctk.CTkLabel(
            rate_container, 
            text="1 USD = IDR (loading...)", 
            font=("Arial", 24, "bold"),
            text_color="#d48a00"
        )
        self.rate_label.pack(pady=(4, 1))
        
        self.rate_time_label = ctk.CTkLabel(
            rate_container, 
            text="", 
            font=("Arial", 16),
            text_color="gray"
        )
        self.rate_time_label.pack(pady=(0, 2))
        
        refresh_rate_btn = ctk.CTkButton(
            rate_container, 
            text="⟳ Refresh", 
            command=self.fetch_usd_idr_rate,
            width=80,
            height=20,
            font=("Arial", 16, "bold")
        )
        refresh_rate_btn.pack(pady=(0, 4))
        
        # ========== FEATURES GRID (2 KOLOM, 5 BARIS) ==========
        features_frame = ctk.CTkFrame(self.main_frame, fg_color="grey")
        features_frame.pack(pady=5, padx=15, fill="x")
        
        ctk.CTkLabel(features_frame, text="✨ Features", font=("Arial", 20, "bold")).pack(pady=2)
        
        # Grid container
        grid_frame = ctk.CTkFrame(features_frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=5)
        
        # UPDATE v1.1: Menampilkan informasi tab Crypto Baru
        features = [
            ("📝 Notes", "Write & share notes"),
            ("💱 Currency", "Real-time rates (Open ER-API)"),
            ("🪙 Crypto", "BTC & ETH Price Monitor"),  # Penanda Fitur Baru v1.1
            ("🧮 Calculator", "Scientific"),
            ("📏 Converter", "Multi-category"),
            ("⚡ Electricity", "Volts, Amps, Watts"),
            ("🚀 Velocity", "km/h, mph, knots"),
            ("💧 Liquid/Gas", "Volume conversions"),
            ("🔗 Share Notes", "WhatsApp, Twitter"),
            ("🎨 Modern UI", "Dark/Light mode")
        ]
        
        row = 0
        col = 0
        for title, desc in features:
            feature_item = ctk.CTkFrame(grid_frame, corner_radius=4)
            feature_item.grid(row=row, column=col, padx=3, pady=2, sticky="nsew")
            
            ctk.CTkLabel(feature_item, text=title, font=("Arial", 18, "bold")).pack(anchor="w", padx=5, pady=(2, 0))
            ctk.CTkLabel(feature_item, text=desc, font=("Arial", 14)).pack(anchor="w", padx=5, pady=(0, 2))
            
            col += 1
            if col >= 2:
                col = 0
                row += 1
        
        for i in range(2):
            grid_frame.grid_columnconfigure(i, weight=1)
        
        # ========== FOOTER ==========
        footer_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", pady=4)
        
        ctk.CTkLabel(
            footer_frame, 
            text="💡 Tip: Switch between tools using the tabs above", 
            font=("Arial", 14),
            text_color="green"
        ).pack()

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("500x400")
    tab = HomeTab(root)
    root.mainloop()