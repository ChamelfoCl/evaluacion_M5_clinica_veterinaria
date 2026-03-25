# -*- coding: utf-8 -*-
# ============================================================
# Genera un PDF con la salida del script clinica_veterinaria.py
# ============================================================
import subprocess
import sys
import os
from fpdf import FPDF

# ---- 1. Ejecutar el script y capturar toda la salida --------
print("Ejecutando clinica_veterinaria.py ...")

resultado = subprocess.run(
    [sys.executable, "clinica_veterinaria.py"],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    cwd=os.path.dirname(os.path.abspath(__file__))
)

salida = resultado.stdout
if resultado.stderr:
    salida += "\n--- ERRORES ---\n" + resultado.stderr

print("Salida capturada. Generando PDF ...")

# ---- 2. Crear el PDF con fpdf2 ------------------------------
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Titulo
pdf.set_font("Helvetica", "B", 16)
pdf.cell(0, 10, "Evaluacion Final - Modulo 3", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.set_font("Helvetica", "", 12)
pdf.cell(0, 8, "Base de Datos para una Clinica Veterinaria", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.set_font("Helvetica", "I", 10)
pdf.cell(0, 6, "Resultado de ejecucion del script clinica_veterinaria.py", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.ln(5)

# Linea separadora
pdf.set_draw_color(100, 100, 100)
pdf.line(10, pdf.get_y(), 200, pdf.get_y())
pdf.ln(6)

# Contenido: cada linea de la salida
pdf.set_font("Courier", "", 9)
for linea in salida.splitlines():
    # Detectar lineas de separacion "===" o "---" para resaltarlas
    linea_limpia = linea.strip()
    if linea_limpia.startswith("==="):
        pdf.set_font("Courier", "B", 9)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 5, linea[:100], new_x="LMARGIN", new_y="NEXT", fill=True)
        pdf.set_font("Courier", "", 9)
    elif linea_limpia.startswith("---"):
        pdf.set_font("Courier", "B", 9)
        pdf.cell(0, 5, linea[:100], new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Courier", "", 9)
    elif linea_limpia.startswith("[OK]"):
        pdf.set_text_color(0, 130, 0)
        pdf.cell(0, 5, linea[:100], new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
    elif linea_limpia.startswith("[ERROR]"):
        pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 5, linea[:100], new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
    else:
        pdf.cell(0, 5, linea[:100], new_x="LMARGIN", new_y="NEXT")

# ---- 3. Guardar el PDF --------------------------------------
nombre_pdf = "resultado_clinica_veterinaria.pdf"
pdf.output(nombre_pdf)
print("[OK] PDF generado: {}".format(nombre_pdf))
