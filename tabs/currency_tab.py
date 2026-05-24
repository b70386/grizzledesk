# tabs/currency_tab.py
import customtkinter as ctk
from tkinter import messagebox
import requests
import json
import os
from datetime import datetime, timedelta

class CurrencyTab:
    def __init__(self, parent):
        self.parent = parent
        self.cache_file = "currency_cache.json"
        self.rates = {}
        self.last_updated = None
        self.supported_currencies = [
            "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "INR", "IDR",
            "KRW", "RUB", "BRL", "MXN", "SGD", "NZD", "TRY", "ZAR", "AED", "SAR",
            "THB", "MYR", "PHP", "VND", "HKD"
        ]
        self.setup_ui()
        self.load_cached_rates()
        self.fetch_rates()
    
    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(self.main_frame, text="Currency Converter", font=("Arial", 24, "bold")).pack(pady=10)
        ctk.CTkLabel(self.main_frame, text="Real-time rates (Frankfurter API)", font=("Arial", 14, "bold"), text_color="green").pack(pady=(0,10))
        
        # Amount
        ctk.CTkLabel(self.main_frame, text="Amount:").pack()
        self.amount_entry = ctk.CTkEntry(self.main_frame, width=300, placeholder_text="Enter amount...")
        self.amount_entry.pack(pady=5)
        self.amount_entry.insert(0, "1")
        
        # From & To currency
        currency_frame = ctk.CTkFrame(self.main_frame)
        currency_frame.pack(pady=10)
        
        ctk.CTkLabel(currency_frame, text="From:").grid(row=0, column=0, padx=5)
        self.from_currency = ctk.CTkComboBox(currency_frame, values=self.supported_currencies, width=120)
        self.from_currency.set("USD")
        self.from_currency.grid(row=0, column=1, padx=5)
        
        self.swap_btn = ctk.CTkButton(currency_frame, text="⇄", command=self.swap_currencies, width=40)
        self.swap_btn.grid(row=0, column=2, padx=10)
        
        ctk.CTkLabel(currency_frame, text="To:").grid(row=0, column=3, padx=5)
        self.to_currency = ctk.CTkComboBox(currency_frame, values=self.supported_currencies, width=120)
        self.to_currency.set("IDR")
        self.to_currency.grid(row=0, column=4, padx=5)
        
        # Convert button
        self.convert_btn = ctk.CTkButton(self.main_frame, text="🔄 Convert", command=self.convert, width=150)
        self.convert_btn.pack(pady=10)
        
        # Result
        self.result_label = ctk.CTkLabel(self.main_frame, text="", font=("Arial", 24, "bold"))
        self.result_label.pack(pady=10)
        
        self.rate_label = ctk.CTkLabel(self.main_frame, text="", font=("Arial", 16, "bold"))
        self.rate_label.pack(pady=5)
        
        self.updated_label = ctk.CTkLabel(self.main_frame, text="", font=("Arial", 16, "bold"))
        self.updated_label.pack(pady=5)
        
        self.refresh_btn = ctk.CTkButton(self.main_frame, text="⟳ Refresh Rates", command=self.fetch_rates, width=150)
        self.refresh_btn.pack(pady=10)
    
    def fetch_live_rate(self, from_curr, to_curr):
        """Fetch exchange rate menggunakan API Frankfurter yang stabil"""
        try:
            url = f"https://api.frankfurter.app/latest?from={from_curr}&to={to_curr}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                rate = data.get("rates", {}).get(to_curr)
                return float(rate)
            return None
        except Exception as e:
            print(f"API Error: {e}")
            return None
    
    def fetch_rates(self):
        self.updated_label.configure(text="🔄 Fetching latest rates...")
        self.refresh_btn.configure(state="disabled")
        
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        
        try:
            rate = self.fetch_live_rate(from_curr, to_curr)
            if rate:
                self.rates[f"{from_curr}_{to_curr}"] = rate
                self.last_updated = datetime.now()
                self.save_cache()
                self.updated_label.configure(text=f"✅ Updated: {self.last_updated.strftime('%H:%M:%S')}")
                self.convert()
            else:
                self.updated_label.configure(text="❌ Failed to fetch rates")
                if not self.rates:
                    messagebox.showerror("Error", "Could not fetch exchange rates. Check internet.")
        except Exception as e:
            self.updated_label.configure(text=f"❌ Error: {str(e)[:30]}")
        
        self.refresh_btn.configure(state="normal")
    
    def load_cached_rates(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    cache = json.load(f)
                    self.rates = cache.get("rates", {})
                    updated_str = cache.get("last_updated", "")
                    if updated_str:
                        self.last_updated = datetime.fromisoformat(updated_str)
                        if datetime.now() - self.last_updated < timedelta(hours=1):
                            self.updated_label.configure(text=f"📅 Cached: {self.last_updated.strftime('%H:%M:%S')}")
                            return True
            except:
                pass
        return False
    
    def save_cache(self):
        if self.rates and self.last_updated:
            cache = {"rates": self.rates, "last_updated": self.last_updated.isoformat()}
            with open(self.cache_file, "w") as f:
                json.dump(cache, f)
    
    def convert(self):
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            self.result_label.configure(text="❌ Invalid amount!")
            return
        
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        cache_key = f"{from_curr}_{to_curr}"
        
        rate = self.rates.get(cache_key)
        if not rate:
            self.fetch_rates()
            return
        
        result = amount * rate
        self.result_label.configure(text=f"{amount:,.0f} {from_curr} = {result:,.0f} {to_curr}")
        #self.rate_label.configure(text=f"1 {from_curr} = {rate:.0f} {to_curr}")
    
    def swap_currencies(self):
        from_val = self.from_currency.get()
        to_val = self.to_currency.get()
        self.from_currency.set(to_val)
        self.to_currency.set(from_val)
        self.convert()