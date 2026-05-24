# tabs/calculator_tab.py
import customtkinter as ctk
import math
import cmath

class CalculatorTab:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.expression = ""
    
    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(self.main_frame, text="🧮 Scientific Calculator", font=("Arial", 24, "bold")).pack(pady=10)
        
        # Display
        self.display_var = ctk.StringVar(value="0")
        self.display = ctk.CTkEntry(
            self.main_frame, 
            textvariable=self.display_var, 
            font=("Arial", 28),
            justify="right",
            height=70,
            state="normal"
        )
        self.display.pack(fill="x", pady=10)
        self.display.bind('<Return>', lambda e: self.calculate())
        
        # Buttons layout
        buttons = [
            ['C', '⌫', '(', ')', '÷'],
            ['7', '8', '9', '*', '√'],
            ['4', '5', '6', '-', 'x²'],
            ['1', '2', '3', '+', '1/x'],
            ['0', '.', 'π', 'e', '='],
            ['sin', 'cos', 'tan', 'log', 'ln']
        ]
        
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(fill="both", expand=True, pady=10)
        
        for row_idx, row in enumerate(buttons):
            for col_idx, btn_text in enumerate(row):
                btn = ctk.CTkButton(
                    self.button_frame,
                    text=btn_text,
                    width=80 if btn_text != '=' else 120,
                    height=60,
                    font=("Arial", 24),
                    command=lambda x=btn_text: self.button_click(x)
                )
                btn.grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky="nsew")
            
            for col_idx in range(len(row)):
                self.button_frame.grid_columnconfigure(col_idx, weight=1)
    
    def button_click(self, value):
        if value == 'C':
            self.expression = ""
            self.update_display("0")
        elif value == '⌫':
            self.expression = self.expression[:-1]
            self.update_display(self.expression or "0")
        elif value == '=':
            self.calculate()
        elif value == '÷':
            self.expression += '/'
            self.update_display(self.expression)
        elif value == '√':
            self.expression += 'math.sqrt('
            self.update_display(self.expression)
        elif value == 'x²':
            self.expression += '**2'
            self.update_display(self.expression)
        elif value == '1/x':
            self.expression += '1/'
            self.update_display(self.expression)
        elif value == 'π':
            self.expression += str(math.pi)
            self.update_display(self.expression)
        elif value == 'e':
            self.expression += str(math.e)
            self.update_display(self.expression)
        elif value == 'sin':
            self.expression += 'math.sin('
            self.update_display(self.expression)
        elif value == 'cos':
            self.expression += 'math.cos('
            self.update_display(self.expression)
        elif value == 'tan':
            self.expression += 'math.tan('
            self.update_display(self.expression)
        elif value == 'log':
            self.expression += 'math.log10('
            self.update_display(self.expression)
        elif value == 'ln':
            self.expression += 'math.log('
            self.update_display(self.expression)
        else:
            self.expression += value
            self.update_display(self.expression)
    
    def update_display(self, text):
        self.display_var.set(text)
    
    def calculate(self):
        try:
            # Handle special case for sqrt
            expr = self.expression
            # Replace math.sqrt with actual sqrt for numbers
            result = eval(expr)
            if isinstance(result, float):
                # Round to avoid floating point errors
                result = round(result, 10)
            self.expression = str(result)
            self.update_display(self.expression)
        except Exception as e:
            self.update_display("Error")
            self.expression = ""