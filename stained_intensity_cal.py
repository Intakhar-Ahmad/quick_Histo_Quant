import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import pandas as pd
import os

class FluorescenceAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Fluorescence Image Intensity Analyzer")

        # Hold originals + metadata
        self.images = [None, None, None]      # (gray_array, filename) or None
        self.stats  = []                      # list of {"Image Name": str, "Average Intensity": float}

        # ── UI: buttons ──────────────────────────────────────────
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Upload Image 1",
                  command=lambda: self.upload_image(0)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Upload Image 2",
                  command=lambda: self.upload_image(1)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Upload Image 3",
                  command=lambda: self.upload_image(2)).pack(side=tk.LEFT, padx=5)

        tk.Button(root, text="Compute Average Intensity",
                  command=self.compute_intensities).pack(pady=5)
        tk.Button(root, text="Download XLS",
                  command=self.download_xls).pack(pady=5)

        # ── UI: preview panels ───────────────────────────────────
        self.panels = []
        img_frame = tk.Frame(root)
        img_frame.pack()
        for _ in range(3):
            panel = tk.Label(img_frame)
            panel.pack(side=tk.LEFT, padx=5)
            self.panels.append(panel)

        # ── UI: stats summary ────────────────────────────────────
        self.stats_label = tk.Label(root, font=("Arial", 12), justify="left")
        self.stats_label.pack(pady=10)

    # ─────────────────────────────────────────────────────────────
    def upload_image(self, idx):
        """Load an image, convert to grayscale if needed, store & preview."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.tif *.tiff")])
        if not file_path:
            return

        # Read with OpenCV (keeps alpha if present)
        img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            messagebox.showerror("Error", f"Could not read image:\n{file_path}")
            return

        # Convert to single‑channel grayscale if needed
        if img.ndim == 3:                    # color or multichannel
            if img.shape[2] == 3:            # BGR → Gray
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            elif img.shape[2] == 4:          # BGRA → Gray
                gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            else:
                messagebox.showerror(
                    "Unsupported",
                    "Unsupported channel count > 4. Please supply standard RGB/RGBA images.")
                return
        else:
            gray = img                       # already grayscale

        self.images[idx] = (gray, os.path.basename(file_path))
        self.show_preview(gray, self.panels[idx])

        # Reset previous calculations
        self.stats = []
        self.stats_label.config(text="")

    # ─────────────────────────────────────────────────────────────
    def compute_intensities(self):
        """Calculate mean grayscale intensity per image."""
        self.stats = []
        summary_lines = []

        for i, item in enumerate(self.images):
            if item is None:
                summary_lines.append(f"Image {i+1}: Not loaded")
                continue

            gray, name = item
            mean_val = float(np.mean(gray))          # 0‑255

            self.stats.append({
                "Image Name": name,
                "Average Intensity": mean_val
            })
            summary_lines.append(
                f"Image {i+1} ({name}): {mean_val:.2f}")

        self.stats_label.config(text="\n".join(summary_lines))

        if not self.stats:
            messagebox.showinfo(
                "No images",
                "Please upload at least one image before computing.")

    # ─────────────────────────────────────────────────────────────
    def download_xls(self):
        if not self.stats:
            messagebox.showwarning(
                "No data", "Please compute intensities first.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Save results as …")
        if not save_path:
            return

        try:
            df = pd.DataFrame(self.stats)
            df.to_excel(save_path, index=False)
            messagebox.showinfo("Success",
                                f"Excel file saved to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error",
                                 f"Could not save file:\n{e}")

    # ─────────────────────────────────────────────────────────────
    def show_preview(self, img_array, panel):
        """Display a 200×200 thumbnail in the given panel."""
        thumb = cv2.resize(img_array, (200, 200),
                           interpolation=cv2.INTER_AREA)
        pil_img = Image.fromarray(thumb)
        tk_img = ImageTk.PhotoImage(pil_img)
        panel.config(image=tk_img)
        panel.image = tk_img        # keep reference to avoid GC

# ── Run the application ──────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = FluorescenceAnalyzer(root)
    root.mainloop()
