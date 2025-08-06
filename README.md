# quick_Histo_Quant
When you just need quick, publication-ready numbers, without firing up ImageJ macros or writing Python from scratch  **quick_Histo_Quant** has you covered:

| Task | Script | What it does |
|------|--------|--------------|
| **Square ROI grab** | `quick_snap.py` | Drag-and-drop an image, click once to preview a resizable square, then export the exact-pixel patch. |
| **Fluorescence intensity** | `stained_intensity_cal.py` | Load up to three stained sections, preview thumbnails, and export average grayscale intensity to Excel. |
| **Stained-area fraction** | `stained_area_cal.py` | Auto-enhance contrast, subtract background, and report % positive vs. negative pixels. |

All three tools run as tiny GUI apps built on **Tkinter** no command-line gymnastics required.

**Requirements:**
- numpy
- pandas
- opencv-python
- pillow
- scikit-image
- tkinterdnd2

