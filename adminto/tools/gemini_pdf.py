# utils/gemini_pdf.py
"""
Convert a scanned IMAGE to a true text PDF:
1) Ask Gemini to return a clean HTML fragment (OCR + layout)
2) Render that HTML to PDF with WeasyPrint

Requires:
  pip install google-generativeai weasyprint pillow
Env:
  set GEMINI_API_KEY=your_key
"""

import os
from typing import Optional
from PIL import Image
from weasyprint import HTML
import google.generativeai as genai
from django.conf import settings

API_KEY = settings.GEMINI_API_KEY
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set.")

# Configure the SDK (your installed version may use v1beta under the hood — that's fine)
genai.configure(api_key=API_KEY)

PROMPT = (
    "Tu es un moteur d'OCR de haute fidélité. "
    "Analyse l'image et renvoie UNIQUEMENT un fragment HTML sémantique propre "
    "(pas de balises <html> ni <body>) avec titres <h1..h6>, paragraphes <p>, "
    "listes <ul>/<ol> et tableaux complets <table>/<thead>/<tbody>/<tr>/<th>/<td>. "
    "Respecte la mise en page et la hiérarchie autant que possible."
)

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff")


def _is_image(path: str) -> bool:
    return str(path).lower().endswith(IMAGE_EXTS)


def _open_image(path: str) -> Image.Image:
    return Image.open(path).convert("RGB")


def _pick_exact_model_name() -> str:
    """
    Ask the API which models are available and pick ONE exact name that:
      - supports generateContent
      - accepts 'image' input
    Prefer 1.5 flash/pro if available. FALLBACK to the first candidate otherwise.
    """
    models = list(genai.list_models())  # materialize generator in some SDK versions

    # build candidate list
    candidates = []
    for m in models:
        gen_ok = "generateContent" in getattr(m, "supported_generation_methods", [])
        modalities = set(getattr(m, "input_modalities", []) or [])
        img_ok = "image" in modalities
        if gen_ok and img_ok:
            candidates.append(m.name)

    if not candidates:
        raise RuntimeError(
            "Aucun modèle Gemini compatible (generateContent + image) n'est disponible pour cette clé. "
            "Vérifie l'API key/projet et les accès à Gemini 1.5."
        )

    # preference order by substring (match the EXACT names returned)
    preferred = ["1.5-flash", "1.5-pro", "pro-vision", "1.0-pro-vision"]
    for tag in preferred:
        for name in candidates:
            if tag in name:
                return name

    # fallback: first compatible model
    return candidates[0]


def _generate_html_with_gemini(img: Image.Image) -> str:
    """
    Use the EXACT model name returned by list_models(). No prefix guessing.
    """
    name = _pick_exact_model_name()
    model = genai.GenerativeModel(name)
    res = model.generate_content([PROMPT, img])
    html = (getattr(res, "text", None) or "").strip()
    if not html:
        raise RuntimeError("Le modèle a répondu sans contenu HTML exploitable.")
    return html


def image_to_pdf_via_gemini(image_path: str) -> bytes:
    """
    Public API:
      - image_path: path to a raster image
      - returns: PDF bytes (text selectable)
    """
    if not _is_image(image_path):
        raise ValueError("Le fichier n'est pas une image.")

    img = _open_image(image_path)
    html_fragment = _generate_html_with_gemini(img)

    html_doc = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <style>
      @page {{ size: A4; margin: 18mm; }}
      body {{
        font-family: "DejaVu Sans", Arial, Helvetica, sans-serif;
        font-size: 12pt;
        line-height: 1.25;
        color: #111;
      }}
      table {{ border-collapse: collapse; width: 100%; }}
      th, td {{ border: 1px solid #444; padding: 4px 6px; vertical-align: top; }}
      h1, h2, h3, h4, h5, h6 {{ margin: 0.35em 0 0.2em; }}
      p {{ margin: 0.25em 0; }}
      ul, ol {{ margin: 0.35em 0 0.35em 1.2em; }}
    </style>
  </head>
  <body>
    {html_fragment}
  </body>
</html>"""

    return HTML(string=html_doc).write_pdf()
