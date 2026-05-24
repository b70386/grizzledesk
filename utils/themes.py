# utils/themes.py
import customtkinter as ctk

def apply_theme(app, theme="dark"):
    if theme == "dark":
        ctk.set_appearance_mode("dark")
    else:
        ctk.set_appearance_mode("light")

def get_theme_colors(theme="dark"):
    if theme == "dark":
        return {
            "bg": "#1a1a2e",
            "fg": "#ffffff",
            "button": "#667eea"
        }
    else:
        return {
            "bg": "#f0f0f0",
            "fg": "#1a1a2e",
            "button": "#667eea"
        }