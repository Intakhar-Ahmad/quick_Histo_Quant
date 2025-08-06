"""
Resizable Square‑Cropper
 • Drag‑and‑drop or load an image.
 • The preview automatically fills the window and rescales when the window
   is resized (aspect ratio preserved).
 • Slider (20 – 2000 px) sets the square crop size; default = 150 px.
 • Click once to preview a red square.
 • “Download Selection” saves the exact‑pixel patch from the full‑resolution
   image.
Requires:
    pip install pillow tkinterdnd2
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk, UnidentifiedImageError
import os

# -------------------- constants --------------------
DEFAULT_SIZE = 200            # default crop side length (pixels)
MIN_SIZE, MAX_SIZE = 20, 2000 # slider limits
START_W, START_H    = 800, 600

class SquareSelectorApp:
    def __init__(self, root: TkinterDnD.Tk):
        self.root = root
        root.title("Square Selector")
        root.geometry(f"{START_W}x{START_H}")

        # ---------- internal state ----------
        self.original_img   = None  # full‑resolution Pillow image
        self.display_img    = None  # scaled preview
        self.tk_img         = None  # PhotoImage for Tk
        self.scale_x = self.scale_y = 1  # display→original factors
        self.selected_coords = None      # (x1,y1,x2,y2) in original pixels
        self.last_click = None           # last click (display coords)
        self.crop_size  = DEFAULT_SIZE

        # ---------- UI ----------
        btn_frame = tk.Frame(root); btn_frame.pack(pady=4)

        tk.Button(btn_frame, text="Upload Image",
                  command=self.open_dialog).pack(side=tk.LEFT, padx=5)

        self.save_btn = tk.Button(btn_frame, text="Download Selection",
                                  command=self.download_selection,
                                  state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.size_var = tk.IntVar(value=self.crop_size)
        tk.Scale(root, from_=MIN_SIZE, to=MAX_SIZE, orient="horizontal",
                 label="Square size (pixels)",
                 variable=self.size_var,
                 command=self.on_size_change
                 ).pack(fill=tk.X, padx=10)

        self.info_lbl = tk.Label(root, text="Load an image to begin")
        self.info_lbl.pack(pady=2)

        self.canvas = tk.Canvas(root, cursor="cross", bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # events
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        root.drop_target_register(DND_FILES)
        root.dnd_bind("<<Drop>>", self.handle_drop)

        # best Pillow resampling filter
        try:
            self.resample = Image.Resampling.LANCZOS
        except AttributeError:
            self.resample = Image.LANCZOS

    # ---------- image loading ----------
    def open_dialog(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff")])
        if path:
            self.load_image(path)

    def handle_drop(self, event):
        path = event.data.strip("{}")
        if os.path.isfile(path) and path.lower().endswith(
            (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff")):
            self.load_image(path)
        else:
            messagebox.showwarning("Invalid file", "Please drop a valid image file.")

    def load_image(self, path):
        try:
            self.original_img = Image.open(path)
            self.selected_coords = None
            self.last_click = None
            self.save_btn.config(state=tk.DISABLED)
            self.update_display_image()
            self.update_info()
        except UnidentifiedImageError:
            messagebox.showerror("Error", f"Cannot open image: {path}")

    # ---------- display helpers ----------
    def update_display_image(self):
        if not self.original_img:
            return
        cw, ch = max(1, self.canvas.winfo_width()), max(1, self.canvas.winfo_height())
        ow, oh = self.original_img.size
        scale = min(cw / ow, ch / oh)  # ≤1 shrinks, >1 enlarges
        new_w, new_h = max(1, int(ow * scale)), max(1, int(oh * scale))

        self.display_img = self.original_img.resize((new_w, new_h), self.resample)
        self.scale_x = ow / new_w
        self.scale_y = oh / new_h

        show_img = (self.display_img.convert("RGB")
                    if self.display_img.mode in ("RGBA", "P")
                    else self.display_img)
        self.tk_img = ImageTk.PhotoImage(show_img)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img, tags="img")

        if self.selected_coords:
            self.draw_rectangle_overlay()

    def on_canvas_resize(self, event):
        if self.original_img:
            self.update_display_image()

    def draw_rectangle_overlay(self):
        left, top, right, bottom = self.selected_coords
        disp_left   = left   / self.scale_x
        disp_top    = top    / self.scale_y
        disp_right  = right  / self.scale_x
        disp_bottom = bottom / self.scale_y
        self.canvas.delete("rect")
        self.canvas.create_rectangle(disp_left, disp_top,
                                     disp_right, disp_bottom,
                                     outline="red", width=2, tag="rect")

    # ---------- interaction ----------
    def update_info(self):
        if self.original_img:
            self.info_lbl.config(text=f"Click to select a {self.crop_size}×{self.crop_size} px square")
        else:
            self.info_lbl.config(text="Load an image to begin")

    def on_size_change(self, val):
        self.crop_size = int(float(val))
        self.update_info()
        if self.last_click:
            self.draw_square_at(*self.last_click)

    def handle_click(self, event):
        if not self.original_img:
            return
        self.last_click = (event.x, event.y)
        self.draw_square_at(event.x, event.y)

    def draw_square_at(self, x_disp, y_disp):
        half = self.crop_size // 2
        cx_orig = int(x_disp * self.scale_x)
        cy_orig = int(y_disp * self.scale_y)

        left   = max(0, cx_orig - half)
        top    = max(0, cy_orig - half)
        right  = min(self.original_img.width,  left + self.crop_size)
        bottom = min(self.original_img.height, top  + self.crop_size)
        left, top = right - self.crop_size, bottom - self.crop_size

        self.selected_coords = (left, top, right, bottom)
        self.save_btn.config(state=tk.NORMAL)
        self.draw_rectangle_overlay()

    # ---------- saving ----------
    def download_selection(self):
        if not (self.original_img and self.selected_coords):
            messagebox.showerror("Error", "No selection or image available.")
            return
        x1, y1, x2, y2 = self.selected_coords
        cropped = self.original_img.crop((x1, y1, x2, y2))

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("TIFF", "*.tif"),
                       ("JPEG", "*.jpg *.jpeg")])
        if save_path:
            try:
                ext = os.path.splitext(save_path)[1].lower().lstrip(".")
                fmt = {"jpg":"JPEG","jpeg":"JPEG","png":"PNG",
                       "tif":"TIFF","tiff":"TIFF"}.get(ext,"PNG")
                cropped.save(save_path, format=fmt)
                messagebox.showinfo("Saved", f"Patch saved as:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Save Failed", str(e))

# -------------------- main --------------------
if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app  = SquareSelectorApp(root)
    root.mainloop()
