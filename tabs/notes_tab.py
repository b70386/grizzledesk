# tabs/notes_tab.py
import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import os
from datetime import datetime
import webbrowser
import urllib.parse
import json

class NotesTab:
    def __init__(self, parent):
        self.parent = parent
        self.db_path = "notes.db"
        self.config_file = "notes_config.json"
        self.current_font_family = "Arial"
        self.current_font_size = 12
        
        self.init_database()
        self.load_config()
        self.setup_ui()
        self.load_notes()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def load_config(self):
        """Load font configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    self.current_font_family = config.get("font_family", "Arial")
                    self.current_font_size = config.get("font_size", 12)
            except:
                pass
    
    def save_config(self):
        """Save font configuration to file"""
        config = {
            "font_family": self.current_font_family,
            "font_size": self.current_font_size
        }
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
        except:
            pass
    
    def apply_font_settings(self):
        """Apply current font settings to the text area"""
        font_tuple = (self.current_font_family, self.current_font_size)
        self.content_text.configure(font=font_tuple)
    
    def change_font_family(self, choice):
        """Change font family"""
        self.current_font_family = choice
        self.apply_font_settings()
        self.save_config()
    
    def change_font_size(self, choice):
        """Change font size"""
        self.current_font_size = int(choice)
        self.apply_font_settings()
        self.save_config()
    
    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel - Notes list
        self.left_frame = ctk.CTkFrame(self.main_frame, width=280)
        self.left_frame.pack(side="left", fill="y", padx=(0, 10))
        
        ctk.CTkLabel(self.left_frame, text="📝 My Notes", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.new_btn = ctk.CTkButton(self.left_frame, text="+ New Note", command=self.new_note)
        self.new_btn.pack(pady=5, padx=10, fill="x")
        
        self.search_entry = ctk.CTkEntry(self.left_frame, placeholder_text="🔍 Search notes...")
        self.search_entry.pack(pady=10, padx=10, fill="x")
        self.search_entry.bind('<KeyRelease>', self.search_notes)
        
        self.notes_listbox = ctk.CTkTextbox(self.left_frame, height=400, state="normal")
        self.notes_listbox.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Right panel - Note editor
        self.right_frame = ctk.CTkFrame(self.main_frame)
        self.right_frame.pack(side="right", fill="both", expand=True)
        
        # Title entry
        self.title_entry = ctk.CTkEntry(self.right_frame, placeholder_text="Note title...", font=("Arial", 14))
        self.title_entry.pack(pady=10, padx=10, fill="x")
        
        # Toolbar for font options
        self.toolbar_frame = ctk.CTkFrame(self.right_frame, height=40)
        self.toolbar_frame.pack(pady=(0, 5), padx=10, fill="x")
        
        # Font family dropdown
        ctk.CTkLabel(self.toolbar_frame, text="Font:", font=("Arial", 10)).pack(side="left", padx=(5, 2))
        
        font_families = ["Arial", "Times New Roman", "Courier New", "Verdana", "Georgia", "Comic Sans MS", "Tahoma", "Segoe UI"]
        self.font_family_combo = ctk.CTkComboBox(
            self.toolbar_frame, 
            values=font_families,
            width=120,
            command=self.change_font_family
        )
        self.font_family_combo.set(self.current_font_family)
        self.font_family_combo.pack(side="left", padx=5)
        
        # Font size dropdown
        ctk.CTkLabel(self.toolbar_frame, text="Size:", font=("Arial", 10)).pack(side="left", padx=5)
        
        font_sizes = ["10", "12", "14", "16", "18", "20", "24", "28", "32", "36"]
        self.font_size_combo = ctk.CTkComboBox(
            self.toolbar_frame, 
            values=font_sizes,
            width=60,
            command=self.change_font_size
        )
        self.font_size_combo.set(str(self.current_font_size))
        self.font_size_combo.pack(side="left", padx=5)
        
        # Separator
        ctk.CTkLabel(self.toolbar_frame, text="|", font=("Arial", 10)).pack(side="left", padx=10)
        
        # Bold button (bonus)
        self.bold_btn = ctk.CTkButton(
            self.toolbar_frame, 
            text="B", 
            width=30, 
            height=25,
            command=self.toggle_bold,
            font=("Arial", 10, "bold")
        )
        self.bold_btn.pack(side="left", padx=2)
        
        # Italic button (bonus)
        self.italic_btn = ctk.CTkButton(
            self.toolbar_frame, 
            text="I", 
            width=30, 
            height=25,
            command=self.toggle_italic,
            font=("Arial", 10, "italic")
        )
        self.italic_btn.pack(side="left", padx=2)
        
        # Content text area
        self.content_text = ctk.CTkTextbox(self.right_frame, height=400)
        self.content_text.pack(fill="both", expand=True, padx=10, pady=5)
        self.apply_font_settings()
        
        # Buttons frame
        self.button_frame = ctk.CTkFrame(self.right_frame)
        self.button_frame.pack(pady=10, padx=10, fill="x")
        
        self.save_btn = ctk.CTkButton(self.button_frame, text="💾 Save", command=self.save_note)
        self.save_btn.pack(side="left", padx=5)
        
        self.delete_btn = ctk.CTkButton(self.button_frame, text="🗑️ Delete", command=self.delete_note, fg_color="#c42b1c")
        self.delete_btn.pack(side="left", padx=5)
        
        self.share_btn = ctk.CTkButton(self.button_frame, text="📤 Share", command=self.share_note)
        self.share_btn.pack(side="left", padx=5)
        
        self.current_note_id = None
        
        # Bind keyboard shortcuts
        self.content_text.bind('<Control-b>', lambda e: self.toggle_bold())
        self.content_text.bind('<Control-i>', lambda e: self.toggle_italic())
        self.content_text.bind('<Control-s>', lambda e: self.save_note())
    
    def toggle_bold(self):
        """Toggle bold formatting for selected text (simple version)"""
        try:
            current_font = self.content_text.cget("font")
            if isinstance(current_font, tuple):
                family, size = current_font[0], current_font[1]
                if "bold" in str(current_font).lower():
                    new_font = (family, size, "normal")
                else:
                    new_font = (family, size, "bold")
                self.content_text.configure(font=new_font)
        except:
            pass
    
    def toggle_italic(self):
        """Toggle italic formatting for selected text (simple version)"""
        try:
            current_font = self.content_text.cget("font")
            if isinstance(current_font, tuple):
                family, size = current_font[0], current_font[1]
                if "italic" in str(current_font).lower():
                    new_font = (family, size, "normal")
                else:
                    new_font = (family, size, "italic")
                self.content_text.configure(font=new_font)
        except:
            pass
    
    def load_notes(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, updated_at FROM notes ORDER BY updated_at DESC")
        notes = cursor.fetchall()
        conn.close()
        
        self.notes_listbox.delete("1.0", "end")
        for note in notes:
            display_text = f"{note[1]}\n📅 {note[2][:10]}\n{'-'*30}\n"
            self.notes_listbox.insert("end", display_text)
        
        self.notes_listbox.bind("<ButtonRelease-1>", self.on_note_select)
    
    def on_note_select(self, event):
        index = self.notes_listbox.index("@%d,%d" % (event.x, event.y))
        line = int(index.split('.')[0])
        note_index = (line - 1) // 3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, content FROM notes ORDER BY updated_at DESC")
        notes = cursor.fetchall()
        conn.close()
        
        if note_index < len(notes):
            self.current_note_id = notes[note_index][0]
            self.title_entry.delete(0, "end")
            self.title_entry.insert(0, notes[note_index][1])
            self.content_text.delete("1.0", "end")
            self.content_text.insert("1.0", notes[note_index][2] or "")
    
    def new_note(self):
        self.current_note_id = None
        self.title_entry.delete(0, "end")
        self.content_text.delete("1.0", "end")
    
    def save_note(self):
        title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", "end-1c")
        
        if not title:
            messagebox.showwarning("Warning", "Title cannot be empty!")
            return
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if self.current_note_id:
            cursor.execute(
                "UPDATE notes SET title=?, content=?, updated_at=? WHERE id=?",
                (title, content, now, self.current_note_id)
            )
        else:
            cursor.execute(
                "INSERT INTO notes (title, content, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (title, content, now, now)
            )
            self.current_note_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        self.load_notes()
        messagebox.showinfo("Success", "Note saved!")
    
    def delete_note(self):
        if not self.current_note_id:
            messagebox.showwarning("Warning", "No note selected!")
            return
        
        if messagebox.askyesno("Confirm", "Delete this note?"):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id=?", (self.current_note_id,))
            conn.commit()
            conn.close()
            self.current_note_id = None
            self.title_entry.delete(0, "end")
            self.content_text.delete("1.0", "end")
            self.load_notes()
            messagebox.showinfo("Success", "Note deleted!")
    
    def search_notes(self, event):
        keyword = self.search_entry.get().strip()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if keyword:
            cursor.execute(
                "SELECT id, title, updated_at FROM notes WHERE title LIKE ? OR content LIKE ? ORDER BY updated_at DESC",
                (f"%{keyword}%", f"%{keyword}%")
            )
        else:
            cursor.execute("SELECT id, title, updated_at FROM notes ORDER BY updated_at DESC")
        
        notes = cursor.fetchall()
        conn.close()
        
        self.notes_listbox.delete("1.0", "end")
        for note in notes:
            display_text = f"{note[1]}\n📅 {note[2][:10]}\n{'-'*30}\n"
            self.notes_listbox.insert("end", display_text)
    
    def share_note(self):
        if not self.current_note_id:
            messagebox.showwarning("Warning", "No note selected!")
            return
        
        title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", "end-1c")
        share_text = f"{title}\n\n{content}"
        
        # Create share window
        share_window = ctk.CTkToplevel(self.parent)
        share_window.title("Share Note")
        share_window.geometry("400x350")
        share_window.grab_set()
        
        ctk.CTkLabel(share_window, text="Share via:", font=("Arial", 14, "bold")).pack(pady=10)
        
        platforms_frame = ctk.CTkFrame(share_window)
        platforms_frame.pack(pady=10, padx=20, fill="x")
        
        platforms = [
            ("📋 Copy to Clipboard", "clipboard"),
            ("📧 Email", "email"),
            ("💬 WhatsApp", "whatsapp"),
            ("📨 Telegram", "telegram"),
            ("🐦 Twitter/X", "twitter"),
            ("📘 Facebook", "facebook")
        ]
        
        for text, platform in platforms:
            btn = ctk.CTkButton(
                platforms_frame, 
                text=text,
                command=lambda p=platform, t=share_text, w=share_window: self.share_to_platform(p, t, w)
            )
            btn.pack(pady=5, fill="x")
    
    def share_to_platform(self, platform, text, window):
        encoded_text = urllib.parse.quote(text)
        
        if platform == "clipboard":
            self.parent.clipboard_clear()
            self.parent.clipboard_append(text)
            messagebox.showinfo("Copied", "Note copied to clipboard!")
            window.destroy()
        elif platform == "email":
            webbrowser.open(f"mailto:?subject=Note&body={encoded_text}")
            window.destroy()
        elif platform == "whatsapp":
            webbrowser.open(f"https://wa.me/?text={encoded_text}")
            window.destroy()
        elif platform == "telegram":
            webbrowser.open(f"https://t.me/share/url?url={encoded_text}")
            window.destroy()
        elif platform == "twitter":
            webbrowser.open(f"https://twitter.com/intent/tweet?text={encoded_text}")
            window.destroy()
        elif platform == "facebook":
            webbrowser.open(f"https://www.facebook.com/sharer/sharer.php?u={encoded_text}")
            window.destroy()