# backend/summarizer.py

import os
import fitz  # PyMuPDF
from PIL import Image
import google.generativeai as genai
import markdown

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

UPLOAD_FOLDER = 'uploads'

def pdf_to_images(pdf_path):
    doc = fitz.open(pdf_path)
    image_paths = []

    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=300)
        img_path = os.path.join(UPLOAD_FOLDER, f"page_{i}.png")
        pix.save(img_path)
        image_paths.append(img_path)

    doc.close()
    return image_paths

import base64

def ocr_with_gemini(image_paths):
    ocr_texts = []

    for img_path in image_paths:
        with open(img_path, "rb") as f:
            img_data = f.read()
            encoded_image = base64.b64encode(img_data).decode("utf-8")

        # Construct the image content in expected format
        image_prompt = {
            "mime_type": "image/png",  # or 'image/jpeg' depending on your image format
            "data": encoded_image
        }

        response = model.generate_content([
            "Extract text from this image clearly.",
            image_prompt
        ])

        ocr_texts.append(response.text.strip())

    return "\n".join(ocr_texts)


def summarize_text(text):
    prompt = f"Summarize the following content into key concepts, main topics, and learning objectives:\n\n{text}"
    response = model.generate_content(prompt)
    return response.text.strip()

def summarize_pdf(pdf_path):
    image_paths = pdf_to_images(pdf_path)
    full_text = ocr_with_gemini(image_paths)
    summary = summarize_text(full_text)
    return markdown.markdown(summary)
