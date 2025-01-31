import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

class PDFEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Basic PDF Editor")
        self.input_file = ""
        # Create GUI buttons
        self.create_widgets()
    def create_widgets(self):
        # Configure style
        style = ttk.Style()
        style.configure("TButton", padding=6, font=('Helvetica', 10))
        # Buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Merge PDFs", command=self.merge_pdfs).grid(row=0, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="Split PDF", command=self.split_pdf).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(btn_frame, text="Add Watermark", command=self.add_watermark).grid(row=0, column=2, padx=10, pady=5)
        ttk.Button(btn_frame, text="Extract Text", command=self.extract_text).grid(row=1, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="Rotate Pages", command=self.rotate_pages).grid(row=1, column=1, padx=10, pady=5)

    # --- Core Functions ---
    def select_input_file(self):
        self.input_file = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    def merge_pdfs(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        if not files:
            return
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not output_path:
            return
        merger = PdfMerger()
        for file in files:
            merger.append(file)
        merger.write(output_path)
        merger.close()
        messagebox.showinfo("Success", "PDFs merged successfully!")
    def split_pdf(self):
        self.select_input_file()
        if not self.input_file:
            return
        output_folder = filedialog.askdirectory()
        if not output_folder:
            return
        reader = PdfReader(self.input_file)
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            with open(f"{output_folder}/page_{i+1}.pdf", "wb") as f:
                writer.write(f)
        messagebox.showinfo("Success", f"Split into {len(reader.pages)} pages!")
    def add_watermark(self):
        self.select_input_file()
        if not self.input_file:
            return
        # Create a temporary watermark PDF
        watermark_text = tk.simpledialog.askstring("Watermark", "Enter watermark text:")
        if not watermark_text:
            return
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Helvetica", 40)
        can.setFillColorRGB(0.5, 0.5, 0.5, alpha=0.3)
        can.drawString(100, 100, watermark_text)
        can.save()
        packet.seek(0)
        watermark_pdf = PdfReader(packet)
        watermark_page = watermark_pdf.pages[0]
        # Apply watermark
        reader = PdfReader(self.input_file)
        writer = PdfWriter()
        for page in reader.pages:
            page.merge_page(watermark_page)
            writer.add_page(page)
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not output_path:
            return
        with open(output_path, "wb") as f:
            writer.write(f)
        messagebox.showinfo("Success", "Watermark added!")
    def extract_text(self):
        self.select_input_file()
        if not self.input_file:
            return
        text = ""
        with pdfplumber.open(self.input_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        # Show text in a new window
        text_window = tk.Toplevel(self.root)
        text_window.title("Extracted Text")
        text_box = tk.Text(text_window, wrap="word")
        text_box.pack(fill="both", expand=True)
        text_box.insert("1.0", text)
        text_box.config(state="disabled")
    def rotate_pages(self):
        self.select_input_file()
        if not self.input_file:
            return
        rotation = tk.simpledialog.askinteger("Rotate Pages", "Enter rotation (90, 180, 270):")
        if not rotation:
            return
        reader = PdfReader(self.input_file)
        writer = PdfWriter()
        for page in reader.pages:
            page.rotate(rotation)
            writer.add_page(page)
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not output_path:
            return
        with open(output_path, "wb") as f:
            writer.write(f)
        messagebox.showinfo("Success", "Pages rotated!")

# --- Run the App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFEditorApp(root)
    root.mainloop()
