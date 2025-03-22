import tkinter as tk
from tkinter import filedialog, messagebox
import ctypes
import pyautogui
import threading
import time
from ai_engine import ask_ollama

# Screen size
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)

# Global state for activity tracking
last_mouse_move = time.time()
auto_collapsed = False

# Geometry and style
full_size = 600
collapsed_size = 40
width = 800
height = 600
dock_position = "Top"
is_expanded = False

bg_color = "black"
corner_radius = 20
transparency_color = "pink"  # used for faking rounded corners

def set_dock_position(pos):
    global dock_position
    dock_position = pos
    apply_geometry()

def apply_geometry():
    global is_expanded, last_mouse_move
    if dock_position == "Top":
        x = (screen_width - width) // 2
        y = 0
        h = full_size if is_expanded else collapsed_size
        root.geometry(f"{width}x{h}+{x}+{y}")
        text_area.config(height=40 if is_expanded else 1)
    elif dock_position == "Bottom":
        x = (screen_width - width) // 2
        h = full_size if is_expanded else collapsed_size
        y = screen_height - h
        root.geometry(f"{width}x{h}+{x}+{y}")
        text_area.config(height=40 if is_expanded else 1)
    elif dock_position == "Left":
        y = (screen_height - height) // 2
        w = full_size if is_expanded else collapsed_size
        root.geometry(f"{w}x{height}+0+{y}")
        text_area.config(width=40 if is_expanded else 5)
    elif dock_position == "Right":
        y = (screen_height - height) // 2
        w = full_size if is_expanded else collapsed_size
        x = screen_width - w
        root.geometry(f"{w}x{height}+{x}+{y}")
        text_area.config(width=40 if is_expanded else 5)

    last_mouse_move = time.time()

def toggle_expand():
    global is_expanded, last_mouse_move
    is_expanded = not is_expanded
    toggle_button.config(text="▲" if is_expanded else "▼")
    last_mouse_move = time.time()
    apply_geometry()

def handle_return_key(event):
    cursor_index = text_area.index("insert")
    line_num = cursor_index.split(".")[0]
    prev_line = text_area.get(f"{int(line_num)-1}.0", f"{int(line_num)-1}.end")

    if prev_line.strip().startswith("•"):
        leading_spaces = len(prev_line) - len(prev_line.lstrip())
        bullet = " " * leading_spaces + "• "
        text_area.insert(cursor_index, "\n" + bullet)
        return "break"  # Prevent default Enter behavior
    else:
        return  # Let default Enter happen


def handle_space_key(event):
    cursor = text_area.index("insert")
    line_start = text_area.get(f"{cursor} linestart", cursor)

    # Match triggers like '-', '.', '~', '>'
    if line_start.strip() in ["-", ".", "~", ">"]:
        text_area.delete(f"{cursor} linestart", cursor)
        text_area.insert(f"{cursor} linestart", "• ")
        return "break"


def new_file():
    text_area.delete(1.0, tk.END)
    title_var.set("Untitled")

def open_file():
    file_path = filedialog.askopenfilename(defaultextension=".txt",
                                           filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "r") as file:
            content = file.read()
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, content)
        title_var.set(file_path.split("/")[-1])
        root.title(f"Notepad - {file_path}")

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(text_area.get(1.0, tk.END))
        title_var.set(file_path.split("/")[-1])
        root.title(f"Notepad - {file_path}")

def exit_app():
    if messagebox.askokcancel("Exit", "Do you really want to exit?"):
        root.destroy()

def round_mask(canvas, x1, y1, x2, y2, r, color):
    canvas.create_polygon(
        x1 + r, y1, x2 - r, y1,
        x2, y1 + r, x2, y2 - r,
        x2 - r, y2, x1 + r, y2,
        x1, y2 - r, x1, y1 + r,
        smooth=True, fill=color, outline=""
    )

def peek_expand():
    global auto_collapsed
    auto_collapsed = False
    apply_geometry()

def auto_collapse():
    global auto_collapsed
    auto_collapsed = True
    if dock_position in ["Top", "Bottom"]:
        root.geometry(f"{width}x5+{root.winfo_x()}+{root.winfo_y()}")
        text_area.config(height=1)
    else:
        root.geometry(f"5x{height}+{root.winfo_x()}+{root.winfo_y()}")
        text_area.config(width=1)

def monitor_inactivity():
    global last_mouse_move, is_expanded, auto_collapsed

    while True:
        x, y = pyautogui.position()
        time.sleep(0.1)

        # Detect mouse movement
        if (x, y) != monitor_inactivity.last_pos:
            last_mouse_move = time.time()
        monitor_inactivity.last_pos = (x, y)

        # Auto-peek if near edge
        if not is_expanded:
            if dock_position == "Top" and y <= 5:
                peek_expand()
            elif dock_position == "Bottom" and y >= screen_height - 5:
                peek_expand()
            elif dock_position == "Left" and x <= 5:
                peek_expand()
            elif dock_position == "Right" and x >= screen_width - 5:
                peek_expand()

        # Auto-collapse if idle
        if time.time() - last_mouse_move > 5 and not is_expanded and not auto_collapsed:
            auto_collapse()






def run_ai():
    text = text_area.get("1.0", "end").strip()
    if not text:
        return
    text_area.insert("end", "\n\n🧠 Thinking...\n")
    root.update()

    response = ask_ollama(text)
    text_area.insert("end", f"\n🤖 {response.strip()}\n")





# Root setup
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", 0.9)  # Transparency
root.config(bg=transparency_color)
root.wm_attributes("-transparentcolor", transparency_color)

# Rounded canvas
canvas = tk.Canvas(root, highlightthickness=0, bg=transparency_color)
canvas.pack(fill="both", expand=True)
round_mask(canvas, 0, 0, width, full_size, corner_radius, bg_color)

# Main container frame
container = tk.Frame(canvas, bg=bg_color)
container.place(relx=0, rely=0, relwidth=1, relheight=1)

# Top bar
top_bar = tk.Frame(container, bg="#111")
top_bar.pack(fill="x")

dock_options = ["Top", "Bottom", "Left", "Right"]
dock_var = tk.StringVar(value="Top")
dock_menu = tk.OptionMenu(top_bar, dock_var, *dock_options, command=set_dock_position)
dock_menu.config(bg="#222", fg="white")
dock_menu.pack(side="left", padx=5, pady=5)

title_var = tk.StringVar(value="Untitled")
title_entry = tk.Entry(top_bar, textvariable=title_var, font=("Segoe UI", 10),
                       bg="#333", fg="white", insertbackground="white", bd=0)
title_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)

toggle_button = tk.Button(top_bar, text="▼", command=toggle_expand, bg="#444", fg="white", width=3)
toggle_button.pack(side="right", padx=2, pady=5)

exit_button = tk.Button(top_bar, text="X", command=exit_app, bg="#a00", fg="white", width=3)
exit_button.pack(side="right", padx=2, pady=5)

ai_button = tk.Button(top_bar, text="🤖 AI", command=run_ai, bg="#005", fg="white")
ai_button.pack(side="right", padx=5, pady=5)
# Text area
text_area = tk.Text(container, font=("Consolas", 12), height=1,
                    bg="#111", fg="white", insertbackground="white", bd=0)
text_area.pack(fill="both", expand=True)
text_area.bind("<Return>", handle_return_key)
text_area.bind("<space>", handle_space_key)  # <<< NEW LINE
text_area.bind("<space>", handle_space_key)



"""
# Menu
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="New", command=new_file)
file_menu.add_command(label="Open...", command=open_file)
file_menu.add_command(label="Save As...", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=exit_app)
menu_bar.add_cascade(label="File", menu=file_menu)
root.config(menu=menu_bar)
"""

# Apply geometry + start tracking
apply_geometry()
monitor_inactivity.last_pos = pyautogui.position()
threading.Thread(target=monitor_inactivity, daemon=True).start()

# Launch app
root.mainloop()
