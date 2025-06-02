import base64
import pandas as pd
from io import BytesIO
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa 

env = Environment(loader=FileSystemLoader("templates"))

def firma_bytes_a_base64(firma_bytes: bytes) -> str:
    return base64.b64encode(firma_bytes).decode("utf-8")

def generar_pdf_reporte(df: pd.DataFrame, firmas: list[dict]) -> bytes:
    """
    Genera un PDF a partir del DataFrame y lista de firmas.
    
    firmas: lista de dicts con formato {"nombre": str, "imagen_base64": str}
    """
    template = env.get_template("report_pdf.html")
    html_content = template.render(
        columnas=df.columns,
        filas=df.values.tolist(),
        firmas=firmas
    )

    pdf_file = BytesIO()
    # Convertir HTML a PDF con pisa
    pisa_status = pisa.CreatePDF(
        src=html_content,
        dest=pdf_file,
        encoding='utf-8'
    )

    if pisa_status.err:
        raise Exception("Error al generar el PDF")

    pdf_file.seek(0)
    return pdf_file.read()
