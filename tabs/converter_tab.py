# tabs/converter_tab.py
import customtkinter as ctk

class ConverterTab:
    def __init__(self, parent):
        self.parent = parent
        
        # Define units FIRST before setup_ui
        self.units = {
            "Length": {
                "Meter": 1,
                "Kilometer": 1000,
                "Centimeter": 0.01,
                "Millimeter": 0.001,
                "Mile": 1609.34,
                "Yard": 0.9144,
                "Foot": 0.3048,
                "Inch": 0.0254,
                "Light Year": 9.461e15
            },
            "Mass": {
                "Kilogram": 1,
                "Gram": 0.001,
                "Milligram": 0.000001,
                "Pound": 0.453592,
                "Ounce": 0.0283495
            },
            "Volume": {
                "Liter": 1,
                "Milliliter": 0.001,
                "Gallon (US)": 3.78541,
                "Quart (US)": 0.946353,
                "Cup": 0.236588
            },
            "Temperature": {
                "Celsius": "celsius",
                "Fahrenheit": "fahrenheit",
                "Kelvin": "kelvin"
            },
            "Electricity": {
                "Volt": 1,
                "Kilovolt": 1000,
                "Millivolt": 0.001,
                "Ampere": 1,
                "Milliampere": 0.001,
                "Ohm": 1,
                "Watt": 1,
                "Kilowatt": 1000,
                "Horsepower": 745.7
            },
            "Velocity": {
                "m/s": 1,
                "km/h": 0.27778,
                "mph": 0.44704,
                "knot": 0.514444,
                "ft/s": 0.3048
            },
            "Liquid/Gas": {
                "Liter": 1,
                "Milliliter": 0.001,
                "Gallon (US)": 3.78541,
                "Gallon (UK)": 4.54609,
                "Cubic Meter": 1000,
                "Cubic Foot": 28.3168,
                "Barrel (Oil)": 158.987
            }
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(self.main_frame, text="📏 Unit Converter", font=("Arial", 24, "bold")).pack(pady=10)
        
        # Category selector
        ctk.CTkLabel(self.main_frame, text="Category:").pack()
        self.categories = ["Length", "Mass", "Volume", "Temperature", "Electricity", "Velocity", "Liquid/Gas"]
        self.category_combo = ctk.CTkComboBox(
            self.main_frame, 
            values=self.categories, 
            command=self.on_category_change,
            width=200
        )
        self.category_combo.set("Length")
        self.category_combo.pack(pady=5)
        
        # Input frame for From/To
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.pack(fill="x", pady=10, padx=20)
        
        # From section
        ctk.CTkLabel(self.input_frame, text="From:", font=("Arial", 16)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.from_unit = ctk.CTkComboBox(
            self.input_frame, 
            values=self.get_units("Length"), 
            width=180
        )
        self.from_unit.grid(row=0, column=1, padx=10, pady=10)
        
        # Swap button
        self.swap_btn = ctk.CTkButton(
            self.input_frame, 
            text="⇄ Swap", 
            command=self.swap_units,
            width=80
        )
        self.swap_btn.grid(row=0, column=2, padx=20, pady=10)
        
        # To section
        ctk.CTkLabel(self.input_frame, text="To:", font=("Arial", 16)).grid(row=0, column=3, padx=10, pady=10, sticky="w")
        self.to_unit = ctk.CTkComboBox(
            self.input_frame, 
            values=self.get_units("Length"), 
            width=180
        )
        self.to_unit.grid(row=0, column=4, padx=10, pady=10)
        
        # Value input
        value_frame = ctk.CTkFrame(self.main_frame)
        value_frame.pack(fill="x", pady=10, padx=20)
        
        ctk.CTkLabel(value_frame, text="Value:", font=("Arial", 16)).pack(side="left", padx=10)
        self.value_entry = ctk.CTkEntry(value_frame, width=200, placeholder_text="Enter value...")
        self.value_entry.pack(side="left", padx=10)
        self.value_entry.insert(0, "1")
        
        # Convert button
        self.convert_btn = ctk.CTkButton(
            self.main_frame, 
            text="🔄 Convert", 
            command=self.convert,
            width=150,
            height=40
        )
        self.convert_btn.pack(pady=15)
        
        # Result display
        self.result_frame = ctk.CTkFrame(self.main_frame)
        self.result_frame.pack(fill="x", pady=10, padx=20)
        
        ctk.CTkLabel(self.result_frame, text="Result:", font=("Arial", 16, "bold")).pack(pady=5)
        self.result_label = ctk.CTkLabel(
            self.result_frame, 
            text="", 
            font=("Arial", 18, "bold"),
            text_color="#667eea"
        )
        self.result_label.pack(pady=5)
        
        # Initialize with default category
        self.on_category_change("Length")
    
    def get_units(self, category):
        """Get list of units for a category"""
        return list(self.units[category].keys())
    
    def on_category_change(self, category):
        """Update unit dropdowns when category changes"""
        units = self.get_units(category)
        self.from_unit.configure(values=units)
        self.to_unit.configure(values=units)
        self.from_unit.set(units[0])
        self.to_unit.set(units[1] if len(units) > 1 else units[0])
        self.convert()
    
    def swap_units(self):
        """Swap from and to units"""
        from_val = self.from_unit.get()
        to_val = self.to_unit.get()
        self.from_unit.set(to_val)
        self.to_unit.set(from_val)
        self.convert()
    
    def convert_temperature(self, value, from_unit, to_unit):
        """Convert temperature between Celsius, Fahrenheit, Kelvin"""
        # Convert to Celsius first
        if from_unit == "Celsius":
            celsius = value
        elif from_unit == "Fahrenheit":
            celsius = (value - 32) * 5/9
        elif from_unit == "Kelvin":
            celsius = value - 273.15
        else:
            return value
        
        # Convert from Celsius to target
        if to_unit == "Celsius":
            return celsius
        elif to_unit == "Fahrenheit":
            return celsius * 9/5 + 32
        elif to_unit == "Kelvin":
            return celsius + 273.15
        
        return value
    
    def format_result(self, value):
        """Format result with appropriate decimal places"""
        if value is None:
            return "0"
        
        # For Light Year, show in scientific notation if too large
        if abs(value) > 1e12 or (0 < abs(value) < 1e-6):
            return f"{value:.6e}"
        
        # Check if it's a whole number (within 0.0001 tolerance)
        if abs(value - round(value)) < 0.0001:
            return f"{int(round(value))}"
        else:
            # Limit to 4 decimal places
            return f"{value:.4f}".rstrip('0').rstrip('.')
    
    def convert(self):
        """Perform unit conversion"""
        try:
            value = float(self.value_entry.get())
        except ValueError:
            self.result_label.configure(text="❌ Invalid value!")
            return
        
        category = self.category_combo.get()
        from_u = self.from_unit.get()
        to_u = self.to_unit.get()
        
        # Temperature conversion (special case)
        if category == "Temperature":
            result = self.convert_temperature(value, from_u, to_u)
            formatted = self.format_result(result)
            self.result_label.configure(text=f"{value} {from_u} = {formatted} {to_u}")
            return
        
        # Standard unit conversion (multiply/divide)
        try:
            # Get conversion factors
            from_factor = self.units[category][from_u]
            to_factor = self.units[category][to_u]
            
            if from_factor == 0 or to_factor == 0:
                self.result_label.configure(text="❌ Conversion error!")
                return
            
            # Convert: value * from_factor / to_factor
            result = value * from_factor / to_factor
            
            formatted = self.format_result(result)
            self.result_label.configure(text=f"{value} {from_u} = {formatted} {to_u}")
            
        except Exception as e:
            self.result_label.configure(text=f"❌ Error: {str(e)[:30]}")