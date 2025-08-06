import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np

class BinaryImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Binary Image Analyzer")
        
        self.image = None
        self.binary_image = None

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Upload Image", command=self.upload_image).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Convert to Binary", command=self.convert_to_binary).pack(side=tk.LEFT, padx=10)

        # Image panel
        self.panel = tk.Label(root)
        self.panel.pack()

        # Stats label
        self.stats_label = tk.Label(root, text="", font=("Arial", 12))
        self.stats_label.pack(pady=10)

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.tif *.tiff")])
        if file_path:
            self.image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            if self.image is not None:
                self.display_image(self.image)

    def convert_to_binary(self):
        if self.image is None:
            messagebox.showwarning("No Image", "Please upload an image first.")
            return
        _, self.binary_image = cv2.threshold(self.image, 127, 255, cv2.THRESH_BINARY)
        self.display_image(self.binary_image)

        # Calculate pixel percentages
        total_pixels = self.binary_image.size
        positive_pixels = np.sum(self.binary_image == 255)
        negative_pixels = np.sum(self.binary_image == 0)
        pos_percent = (positive_pixels / total_pixels) * 100
        neg_percent = (negative_pixels / total_pixels) * 100

        self.stats_label.config(text=f"Positive Pixels: {pos_percent:.2f}%\nNegative Pixels: {neg_percent:.2f}%")

    def display_image(self, img_array):
        image = Image.fromarray(img_array)
        image = image.resize((400, 400))
        photo = ImageTk.PhotoImage(image=image)
        self.panel.config(image=photo)
        self.panel.image = photo

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = BinaryImageApp(root)
    root.mainloop()
