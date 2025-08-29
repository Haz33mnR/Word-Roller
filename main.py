import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import random
import time
import threading
import os
import sys
import requests
import subprocess
import webbrowser

# -------------------- Version / GitHub --------------------
VERSION = "1.0.0"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/Haz33mnR/Word-Roller/main/version.txt"
UPDATE_URL = "https://raw.githubusercontent.com/Haz33mnR/Word-Roller/main/main.py"
GITHUB_PAGE = "https://github.com/Haz33mnR/Word-Roller"

INSTALLED_VERSION_FILE = "installed_version.txt"

# Read installed version
if os.path.exists(INSTALLED_VERSION_FILE):
    with open(INSTALLED_VERSION_FILE, "r") as f:
        INSTALLED_VERSION = f.read().strip()
else:
    INSTALLED_VERSION = VERSION

# -------------------- File Handling --------------------
def create_roll_file():
    filename = filedialog.asksaveasfilename(
        defaultextension=".roll",
        filetypes=[("Roll files", "*.roll")]
    )
    if not filename:
        return None

    words = []
    while True:
        word = simpledialog.askstring("Add Word", "Enter a word (or leave empty to finish):")
        if not word:
            break
        words.append(word)

    if words:
        with open(filename, "w", encoding="utf-8") as f:
            for w in words:
                f.write(w + "\n")
        messagebox.showinfo("Saved", f"✅ Roll file saved as {filename}")
        return filename
    return None

def load_roll_file():
    filename = filedialog.askopenfilename(
        defaultextension=".roll",
        filetypes=[("Roll files", "*.roll")]
    )
    return filename

# -------------------- Rolling Animation --------------------
def rolling_animation(words, label):
    def run():
        delay = 0.05
        for _ in range(25):
            word = random.choice(words)
            label.config(text=word)
            time.sleep(delay)
            delay += 0.02
        chosen = random.choice(words)
        label.config(text=f"🎉 Final: {chosen}")
    threading.Thread(target=run).start()

def start_roll(filename, label):
    if not filename:
        return
    with open(filename, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]
    if not words:
        messagebox.showerror("Error", "⚠️ No words found in this file!")
        return
    rolling_animation(words, label)

# -------------------- Editor --------------------
def edit_roll_file(filename):
    if not filename or not os.path.exists(filename):
        messagebox.showerror("Error", "File not found!")
        return

    editor = tk.Toplevel()
    editor.title(f"Editing {os.path.basename(filename)}")
    editor.geometry("400x300")

    with open(filename, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]

    listbox = tk.Listbox(editor, selectmode=tk.SINGLE, font=("Arial", 12))
    listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    for w in words:
        listbox.insert(tk.END, w)

    def add_word():
        word = simpledialog.askstring("Add Word", "Enter a new word:")
        if word:
            listbox.insert(tk.END, word)

    def remove_word():
        sel = listbox.curselection()
        if sel:
            listbox.delete(sel[0])
        else:
            messagebox.showwarning("Warning", "No word selected!")

    def save_changes():
        words = listbox.get(0, tk.END)
        with open(filename, "w", encoding="utf-8") as f:
            for w in words:
                f.write(w + "\n")
        messagebox.showinfo("Saved", "✅ Changes saved!")

    btn_frame = tk.Frame(editor)
    btn_frame.pack(pady=5)

    tk.Button(btn_frame, text="➕ Add Word", command=add_word).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="❌ Remove Word", command=remove_word).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="💾 Save Changes", command=save_changes).grid(row=0, column=2, padx=5)

# -------------------- Credits --------------------
def show_credits():
    messagebox.showinfo(
        "Credits",
        f"🎲 Word Roller App\n"
        f"Version: {INSTALLED_VERSION}\n\n"
        f"Made by: Haz33mn\n"
        f"Special thanks to: ChatGPT\n\n"
        f"🔗 GitHub: {GITHUB_PAGE}"
    )

# -------------------- Update --------------------
def check_for_updates():
    try:
        response = requests.get(GITHUB_VERSION_URL, timeout=5)
        if response.status_code == 200:
            latest_version = response.text.strip()
            if latest_version > INSTALLED_VERSION:
                if messagebox.askyesno(
                    "Update Available",
                    f"New version {latest_version} available!\n"
                    f"You are on {INSTALLED_VERSION}.\n\n"
                    "Do you want to update automatically?"
                ):
                    auto_update(latest_version)
            else:
                messagebox.showinfo("Update Check", "✅ You already have the latest version!")
        else:
            messagebox.showerror("Error", "⚠️ Failed to check updates from GitHub.")
    except Exception as e:
        messagebox.showerror("Error", f"⚠️ Could not connect:\n{e}")

def auto_update(new_version):
    try:
        response = requests.get(UPDATE_URL, timeout=10)
        if response.status_code == 200:
            with open(sys.argv[0], "wb") as f:
                f.write(response.content)
            with open(INSTALLED_VERSION_FILE, "w") as f:
                f.write(new_version)
            messagebox.showinfo("Update Complete", "✅ Update installed, restarting app...")
            subprocess.Popen([sys.executable] + sys.argv)
            sys.exit(0)
        else:
            messagebox.showerror("Update Failed", "⚠️ Failed to download update.")
    except Exception as e:
        messagebox.showerror("Update Failed", f"⚠️ Could not update:\n{e}")

# -------------------- Main App --------------------
def main():
    root = tk.Tk()
    root.title("Word Roller")
    root.geometry("420x300")

    label = tk.Label(root, text="🎲 Ready to roll!", font=("Arial", 18))
    label.pack(pady=20)

    tk.Button(root, text="➕ Create New Roll File", command=lambda: start_roll(create_roll_file(), label), width=25).pack(pady=5)
    tk.Button(root, text="🎲 Load & Roll", command=lambda: start_roll(load_roll_file(), label), width=25).pack(pady=5)
    tk.Button(root, text="✏️ Edit Existing Roll File", command=lambda: edit_roll_file(load_roll_file()), width=25).pack(pady=5)
    tk.Button(root, text="🔄 Check for Updates", command=check_for_updates, width=25).pack(pady=5)
    tk.Button(root, text="ℹ️ Credits", command=show_credits, width=25).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()

