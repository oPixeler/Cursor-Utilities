import tkinter as tk
from tkinter import ttk
from pynput import mouse
from pynput.mouse import Listener
import pyautogui
import math
import io
import win32clipboard
from PIL import ImageGrab

# Global variables
ruler_lengths = []
ruler_start_x = 0
ruler_start_y = 0
is_button_pressed = False
lines = []
text_labels = []

# Tkinter window setup
root = tk.Tk()
root.title('Pixel Information')
root.configure(bg='#000000')

# Style configuration
style = ttk.Style()
style.configure('TLabel', background='#2e2e2e', foreground='black', font=('Arial', 14, 'bold'))
style.configure('TButton', font=('Arial', 12, 'bold'), padding=10)

# GUI for pixel information
frame = ttk.Frame(root, padding=20)
frame.pack(pady=20)

# Title label
title_label = ttk.Label(frame, text='Mouse Information:', font=('Arial', 16, 'bold'), foreground='pink', background='#2e2e2e')
title_label.pack(pady=5)

# Separator line
separator = ttk.Label(frame, text='-' * 30, background='#2e2e2e', foreground='white')
separator.pack(pady=5)

# Position label
coord_label = ttk.Label(frame, text='Position: (0, 0)', background='#3a3a3a', foreground='white', font=('Arial', 14))
coord_label.pack(pady=5, padx=10, fill=tk.X)

# Color label
color_label = ttk.Label(frame, text='Colour: #000000', background='#3a3a3a', foreground='white', font=('Arial', 14))
color_label.pack(pady=5, padx=10, fill=tk.X)

# Overlay window and canvas declarations
overlay_window = None
overlay_canvas = None

def spawn_canvas():
    global overlay_window, overlay_canvas
    overlay_window = tk.Toplevel(root)
    overlay_window.title("Measurement Overlay")
    overlay_window.geometry("800x600")
    overlay_window.attributes("-topmost", True)
    overlay_window.attributes("-fullscreen", True)

    overlay_canvas = tk.Canvas(overlay_window, bg="#1e1e1e", highlightthickness=0)
    overlay_canvas.pack(fill="both", expand=True)

    # Set the overlay to be translucent
    overlay_window.attributes("-alpha", 0.7)

    # Add a button to take a screenshot and close the canvas
    screenshot_button = ttk.Button(overlay_canvas, text="Take Screenshot", command=take_screenshot_and_close)
    screenshot_button.grid(row=1, column=0, sticky="nsew")

    # Bind mouse motion to the overlay canvas
    overlay_canvas.bind("<Motion>", lambda event: on_move(event.x, event.y))

    # Start listening for mouse clicks
    listener = Listener(on_click=on_click)
    listener.start()

    # Focus on the canvas to capture mouse events
    overlay_canvas.focus_set()

def take_screenshot_and_close():
    take_screenshot_and_copy()
    overlay_window.destroy()

def take_screenshot_and_copy():
    if overlay_canvas is None:
        return

    screenshot = ImageGrab.grab()
    screenshot_path = "screenshot.png"
    screenshot.save(screenshot_path, format="PNG")

    output = io.BytesIO()
    screenshot.save(output, format="BMP")
    data = output.getvalue()[14:]
    output.close()

    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
    except Exception as e:
        print(f"Failed to copy image to clipboard: {e}")

def on_click(x, y, button, pressed):
    global ruler_start_x, ruler_start_y, is_button_pressed
    if overlay_canvas is None:
        return

    if button == mouse.Button.left:
        if pressed:
            is_button_pressed = True
            ruler_start_x, ruler_start_y = x, y
            line = overlay_canvas.create_line(x, y, x, y, fill="cyan", width=4)
            lines.append(line)
        else:
            is_button_pressed = False
            if lines:
                end_x, end_y = x, y
                ruler_length = math.sqrt((end_x - ruler_start_x)**2 + (end_y - ruler_start_y)**2)
                ruler_lengths.append(ruler_length)
                overlay_canvas.coords(lines[-1], ruler_start_x, ruler_start_y, end_x, end_y)

                mid_x = (ruler_start_x + end_x) / 2
                mid_y = (ruler_start_y + end_y) / 2
                text_label = overlay_canvas.create_text(mid_x, mid_y, text=f"{ruler_length:.2f} px", fill="yellow", font=('Arial', 12, 'bold'))
                text_labels.append(text_label)

def on_move(x, y):
    if is_button_pressed and overlay_canvas is not None and lines:
        overlay_canvas.coords(lines[-1], ruler_start_x, ruler_start_y, x, y)

def get_pixel_info():
    mouse_x, mouse_y = pyautogui.position()
    pixel_color = pyautogui.pixel(mouse_x, mouse_y)
    hex_color = '#%02x%02x%02x' % pixel_color
    coord_label.config(text=f'Position: ({mouse_x}, {mouse_y})')
    color_label.config(text=f'Colour: {hex_color}')
    root.after(100, get_pixel_info)

# Bind 's' key to spawn the canvas and 'f' key to close the pixel info window
root.bind('s', lambda event: spawn_canvas())
root.bind('<f>', lambda event: root.destroy())

# Start the main event loop
get_pixel_info()
root.mainloop()