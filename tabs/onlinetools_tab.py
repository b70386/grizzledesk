# tabs/onlinetools_tab.py
import customtkinter as ctk
import webbrowser
import os
import sys
from PIL import Image

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class OnlineToolsTab:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
    
    def load_icon(self, name, size=(48, 48)):
        """Load icon from assets folder"""
        # Try different file extensions
        extensions = ['_3d.png', '.png', '.ico']
        for ext in extensions:
            path = resource_path(os.path.join("assets", f"{name}{ext}"))
            if os.path.exists(path):
                try:
                    return ctk.CTkImage(light_image=Image.open(path), 
                                       dark_image=Image.open(path), 
                                       size=size)
                except:
                    pass
        return None
    
    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            self.main_frame, 
            text="🌐 Online Tools - Quick Access", 
            font=("Arial", 24, "bold")
        ).pack(pady=10)
        
        ctk.CTkLabel(
            self.main_frame, 
            text="Click any tool to open in your default browser",
            font=("Arial", 14),
            text_color="gray"
        ).pack(pady=(0, 20))
        
        # Create a center frame to hold the tools
        self.center_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.center_frame.pack(expand=True, fill="both")
        
        # Tools data
        self.tools = [
            ("GitHub", "github", "https://github.com/"),
            ("Python", "python", "https://www.python.org/"),
            ("Cobalt", "cobalt", "https://cobalt.tools/"),
            ("Hybrid Analysis", "hybrid", "https://www.hybrid-analysis.com/"),
            ("VirusTotal", "virustotal", "https://www.virustotal.com/"),
            ("iLovePDF", "ilovepdf", "https://www.ilovepdf.com/"),
            ("iLoveIMG", "iloveimg", "https://www.iloveimg.com/"),
            ("BrowserLeaks", "browserleaks", "https://browserleaks.com/"),
            ("Fast.com", "fast", "https://fast.com/"),
            ("ScamAdviser", "scamadviser", "https://www.scamadviser.com/")
        ]
        
        # Create button frame (this will be centered)
        self.button_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.button_frame.pack(expand=True)
        
        # Grid configuration: 2 rows x 5 columns
        rows = 2
        cols = 5
        
        for idx, (name, icon_name, url) in enumerate(self.tools):
            row = idx // cols
            col = idx % cols
            
            icon = self.load_icon(icon_name)
            
            if icon:
                btn = ctk.CTkButton(
                    self.button_frame,
                    image=icon,
                    text=name,
                    compound="top",
                    width=130,
                    height=130,
                    corner_radius=15,
                    command=lambda u=url: webbrowser.open(u)
                )
            else:
                # Fallback: text-only button
                btn = ctk.CTkButton(
                    self.button_frame,
                    text=f"🌐\n{name}",
                    compound="top",
                    width=130,
                    height=130,
                    corner_radius=15,
                    command=lambda u=url: webbrowser.open(u)
                )
            
            btn.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        
        # Configure grid weights to center content
        for i in range(cols):
            self.button_frame.grid_columnconfigure(i, weight=1)
        for i in range(rows):
            self.button_frame.grid_rowconfigure(i, weight=1)
        
        # Center the button_frame within center_frame
        self.center_frame.grid_rowconfigure(0, weight=1)
        self.center_frame.grid_columnconfigure(0, weight=1)
        
        # Info label at bottom
        info_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        info_frame.pack(side="bottom", fill="x", pady=20)
        
        ctk.CTkLabel(
            info_frame,
            text="💡 Tip: All icons are official favicons from respective websites",
            font=("Arial", 14),
            text_color="green"
        ).pack()