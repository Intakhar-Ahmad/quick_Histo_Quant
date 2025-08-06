import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import pandas as pd
import os

class BinaryImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi Image Binary Analyzer")

        self.images = [None, None, None]
        self.binaries = [None, None, None]
        self.stats = []

        # Buttons to load images
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Upload Image 1", command=lambda: self.upload_image(0)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Upload Image 2", command=lambda: self.upload_image(1)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Upload Image 3", command=lambda: self.upload_image(2)).pack(side=tk.LEFT, padx=5)

        # Buttons to process and export
        tk.Button(root, text="Convert All to Binary", command=self.convert_all_to_binary).pack(pady=5)
        tk.Button(root, text="Download XLS", command=self.download_xls).pack(pady=5)

        # Image preview panels
        self.panels = []
        image_frame = tk.Frame(root)
        image_frame.pack()
        for _ in range(3):
            panel = tk.Label(image_frame)
            panel.pack(side=tk.LEFT, padx=5)
            self.panels.append(panel)

        # Statistics display
        self.stats_label = tk.Label(root, text="", font=("Arial", 12), justify="left")
        self.stats_label.pack(pady=10)

    def upload_image(self, idx):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.tif *.tiff")])
        if file_path:
            image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            if image is not None:
                self.images[idx] = (image, os.path.basename(file_path))
                self.display_image(image, self.panels[idx])
                self.stats = []  # Reset previous stats

    def convert_all_to_binary(self):
        self.stats = []
        summary = ""

        for i, item in enumerate(self.images):
            if item is None:
                summary += f"Image {i+1}: Not loaded\n"
                continue

            image, name = item
            _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
            self.binaries[i] = binary
            self.display_image(binary, self.panels[i])

            total_pixels = binary.size
            positive_pixels = np.sum(binary == 255)
            negative_pixels = np.sum(binary == 0)
            pos_percent = (positive_pixels / total_pixels) * 100
            neg_percent = (negative_pixels / total_pixels) * 100

            self.stats.append({
                "Image Name": name,
                "Total Pixels": total_pixels,
                "Positive Pixels (%)": pos_percent,
                "Negative Pixels (%)": neg_percent
            })

            summary += f"Image {i+1} ({name}):\n  Total: {total_pixels}, +: {pos_percent:.2f}%, -: {neg_percent:.2f}%\n"

        self.stats_label.config(text=summary)

    def download_xls(self):
        if not self.stats:
            messagebox.showwarning("No Data", "Please convert images first.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if save_path:
            df = pd.DataFrame(self.stats)
            try:
                df.to_excel(save_path, index=False)
                messagebox.showinfo("Success", f"Excel file saved to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{e}")

    def display_image(self, img_array, panel):
        image = Image.fromarray(img_array)
        image = image.resize((200, 200))
        photo = ImageTk.PhotoImage(image=image)
        panel.config(image=photo)
        panel.image = photo  # keep reference

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = BinaryImageApp(root)
    root.mainloop()
