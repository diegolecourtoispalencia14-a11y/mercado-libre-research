#!/usr/bin/env python3
"""
Generador de Planos de Fabricación y Producción para Juego de 3 Repisas Flotantes
Salida: /Users/dlpo.c./Desktop/PLANOS_PRODUCCION_REPISAS_FLOTANTES.pdf
Versión 2.0: Geometría corregida, sin solapamientos, escala precisa CAD.
"""

import os
import math
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas

PDF_PATH = "/Users/dlpo.c./Desktop/PLANOS_PRODUCCION_REPISAS_FLOTANTES.pdf"

# Paleta técnica de ingeniería
C_BORDER_FRAME = colors.HexColor("#1E293B")
C_TITLE_BG = colors.HexColor("#0F172A")
C_TEXT_MAIN = colors.HexColor("#0F172A")
C_TEXT_MUTED = colors.HexColor("#475569")
C_DIM_LINE = colors.HexColor("#DC2626")  # Rojo técnico para cotas
C_DIM_TEXT = colors.HexColor("#991B1B")
C_PIECE_FILL = colors.HexColor("#F8FAFC")
C_PIECE_STROKE = colors.HexColor("#1E293B")
C_EDGE_BAND = colors.HexColor("#2563EB")  # Azul para cantos con cubrecanto
C_DRILL_FILL = colors.HexColor("#FEF08A")
C_DRILL_CENTER = colors.HexColor("#EF4444")

PAGE_W, PAGE_H = landscape(letter)  # 792 x 612 pt


def draw_arrow(c, x, y, angle_rad, length=4.5, width=2.2):
    """Dibuja una punta de flecha técnica orientada."""
    c.saveState()
    c.translate(x, y)
    c.rotate(math.degrees(angle_rad))
    p = c.beginPath()
    p.moveTo(0, 0)
    p.lineTo(-length, width)
    p.lineTo(-length, -width)
    p.close()
    c.setFillColor(C_DIM_LINE)
    c.setStrokeColor(C_DIM_LINE)
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


def draw_dim_h(c, x1, x2, y, text, offset=11, text_above=True, font_size=6.5):
    """Cota horizontal con líneas de extensión y flechas."""
    c.saveState()
    c.setStrokeColor(C_DIM_LINE)
    c.setLineWidth(0.5)

    dim_y = y + offset
    c.line(x1, y - 1, x1, dim_y + (2 if offset > 0 else -2))
    c.line(x2, y - 1, x2, dim_y + (2 if offset > 0 else -2))
    c.line(x1, dim_y, x2, dim_y)

    draw_arrow(c, x1, dim_y, 0)
    draw_arrow(c, x2, dim_y, math.pi)

    c.setFont("Helvetica-Bold", font_size)
    c.setFillColor(C_DIM_TEXT)
    mid_x = (x1 + x2) / 2
    ty = dim_y + 2 if text_above else dim_y - 7
    c.drawCentredString(mid_x, ty, str(text))
    c.restoreState()


def draw_dim_v(c, x, y1, y2, text, offset=11, text_right=True, font_size=6.5):
    """Cota vertical con líneas de extensión y flechas."""
    c.saveState()
    c.setStrokeColor(C_DIM_LINE)
    c.setLineWidth(0.5)

    dim_x = x + offset if text_right else x - offset
    c.line(x - 1, y1, dim_x + (2 if text_right else -2), y1)
    c.line(x - 1, y2, dim_x + (2 if text_right else -2), y2)
    c.line(dim_x, y1, dim_x, y2)

    draw_arrow(c, dim_x, y1, math.pi / 2)
    draw_arrow(c, dim_x, y2, -math.pi / 2)

    c.setFont("Helvetica-Bold", font_size)
    c.setFillColor(C_DIM_TEXT)
    mid_y = (y1 + y2) / 2
    c.saveState()
    c.translate(dim_x + 3 if text_right else dim_x - 7, mid_y)
    c.rotate(90)
    c.drawCentredString(0, 0, str(text))
    c.restoreState()
    c.restoreState()


def draw_title_block(c, sheet_num, total_sheets, sheet_title, scale_desc):
    """Cajetín de ingeniería y marco perimetral reglamentario."""
    margin = 24
    w = PAGE_W - 2 * margin
    h = PAGE_H - 2 * margin

    # Marco exterior grueso
    c.setStrokeColor(C_BORDER_FRAME)
    c.setLineWidth(1.2)
    c.rect(margin, margin, w, h)

    # Marco interior fino
    c.setLineWidth(0.4)
    c.rect(margin + 3, margin + 3, w - 6, h - 6)

    # Cajetín en esquina inferior derecha
    cb_w = 340
    cb_h = 72
    cb_x = margin + w - cb_w - 3
    cb_y = margin + 3

    c.setFillColor(colors.white)
    c.setStrokeColor(C_BORDER_FRAME)
    c.setLineWidth(0.8)
    c.rect(cb_x, cb_y, cb_w, cb_h, fill=1, stroke=1)

    # Encabezado cajetín
    c.setFillColor(C_TITLE_BG)
    c.rect(cb_x, cb_y + cb_h - 17, cb_w, 17, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(cb_x + 8, cb_y + cb_h - 12, "EXPEDIENTE TÉCNICO DE PRODUCCIÓN INDUSTRIAL")
    c.drawRightString(cb_x + cb_w - 8, cb_y + cb_h - 12, "REV. 2.0 • NOV 2026")

    # Líneas divisorias internas
    c.setStrokeColor(colors.HexColor("#CBD5E1"))
    c.setLineWidth(0.5)
    c.line(cb_x, cb_y + 36, cb_x + cb_w, cb_y + 36)
    c.line(cb_x + 195, cb_y, cb_x + 195, cb_y + 36)

    # Fila superior interna
    c.setFillColor(C_TEXT_MUTED)
    c.setFont("Helvetica-Bold", 5.5)
    c.drawString(cb_x + 8, cb_y + 45, "PROYECTO:")
    c.setFillColor(C_TEXT_MAIN)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(cb_x + 58, cb_y + 45, "JUEGO DE 3 REPISAS FLOTANTES ESCALONADAS")

    # Fila media
    c.setFillColor(C_TEXT_MUTED)
    c.setFont("Helvetica-Bold", 5.5)
    c.drawString(cb_x + 8, cb_y + 26, "PLANO:")
    c.drawString(cb_x + 203, cb_y + 26, "MATERIAL:")

    c.setFillColor(C_TEXT_MAIN)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(cb_x + 42, cb_y + 26, sheet_title)
    c.drawString(cb_x + 242, cb_y + 26, "Melamina 16mm")

    # Fila inferior
    c.setFillColor(C_TEXT_MUTED)
    c.setFont("Helvetica-Bold", 5.5)
    c.drawString(cb_x + 8, cb_y + 9, "ESCALA / COTAS:")
    c.drawString(cb_x + 203, cb_y + 9, "HOJA:")

    c.setFillColor(C_TEXT_MAIN)
    c.setFont("Helvetica", 6.8)
    c.drawString(cb_x + 72, cb_y + 9, f"{scale_desc}  |  Unidades en mm")
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(cb_x + 235, cb_y + 9, f"{sheet_num} DE {total_sheets}")

    # Membrete institucional izquierdo
    c.setFillColor(C_BORDER_FRAME)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(margin + 12, margin + 14, "DIRECCIÓN DE OPERACIONES & MANUFACTURA E-COMMERCE")
    c.setFont("Helvetica", 6.5)
    c.setFillColor(C_TEXT_MUTED)
    c.drawString(margin + 12, margin + 5, "Tolerancia dimensional: ±0.5 mm  •  Barrenado 90° ±0.3°  •  Aprobado para Mercado Envíos Full")


def page_1_pieces(c):
    """Página 1: Planos dimensionales de las 3 piezas y cotas de barrenado."""
    draw_title_block(c, 1, 3, "DESPIECE TÉCNICO Y BARRENADO", "Escala Gráfica")

    # Encabezado de lámina
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(C_TEXT_MAIN)
    c.drawString(36, 562, "PLANO 01: DIMENSIONES GENERALES Y LOCALIZACIÓN DE BARRENOS")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(C_TEXT_MUTED)
    c.drawString(36, 550, "Cotas en milímetros (mm). Línea azul perimetral = Cubrecanto PVC 19x0.45 mm obligatorio.")

    # Escala para piezas: 1 mm = 0.44 pt
    SCALE = 0.44
    SHELF_D = 150 * SCALE  # 66 pt
    THICKNESS = 16 * SCALE * 1.6  # 11.2 pt para visualización clara

    top_y = 430
    canto_y = top_y - 28

    # -------------------------------------------------------------
    # 1. REPISA CHICA (300 x 150 mm)
    # -------------------------------------------------------------
    x_c = 45
    w_c = 300 * SCALE  # 132 pt

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(C_TEXT_MAIN)
    c.drawString(x_c, top_y + SHELF_D + 20, "PIEZA 1: CHICA (300 x 150 mm)")

    # Planta
    c.setFillColor(C_PIECE_FILL)
    c.setStrokeColor(C_EDGE_BAND)
    c.setLineWidth(1.6)
    c.rect(x_c, top_y, w_c, SHELF_D, fill=1, stroke=1)

    # Canto trasero con barrenos
    c.setFillColor(colors.HexColor("#E2E8F0"))
    c.setStrokeColor(C_PIECE_STROKE)
    c.setLineWidth(0.8)
    c.rect(x_c, canto_y, w_c, THICKNESS, fill=1, stroke=1)

    # Eje centro
    c.setStrokeColor(C_DRILL_CENTER)
    c.setLineWidth(0.4)
    c.setDash([3, 2])
    c.line(x_c - 4, canto_y + THICKNESS / 2, x_c + w_c + 4, canto_y + THICKNESS / 2)
    c.setDash([])

    # Barrenos Chica: a 50 mm de orillas, 200 mm entre centros
    c_h1 = x_c + 50 * SCALE
    c_h2 = x_c + 250 * SCALE
    dr = (10 * SCALE) / 2

    for hx in [c_h1, c_h2]:
        c.setFillColor(C_DRILL_FILL)
        c.setStrokeColor(C_DIM_LINE)
        c.setLineWidth(0.6)
        c.circle(hx, canto_y + THICKNESS / 2, dr, fill=1, stroke=1)

        # Proyección oculta en planta
        c.setDash([2, 2])
        c.rect(hx - dr, top_y, 2 * dr, 105 * SCALE, fill=0, stroke=1)
        c.setDash([])

    # Cotas Chica
    draw_dim_h(c, x_c, x_c + w_c, top_y + SHELF_D, "300 mm", offset=8)
    draw_dim_v(c, x_c + w_c, top_y, top_y + SHELF_D, "150", offset=8)
    draw_dim_h(c, x_c, c_h1, canto_y, "50", offset=-11, text_above=False)
    draw_dim_h(c, c_h1, c_h2, canto_y, "200 mm", offset=-11, text_above=False)
    draw_dim_h(c, c_h2, x_c + w_c, canto_y, "50", offset=-11, text_above=False)

    # -------------------------------------------------------------
    # 2. REPISA MEDIANA (400 x 150 mm)
    # -------------------------------------------------------------
    x_m = 235
    w_m = 400 * SCALE  # 176 pt

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(C_TEXT_MAIN)
    c.drawString(x_m, top_y + SHELF_D + 20, "PIEZA 2: MEDIANA (400 x 150 mm)")

    # Planta
    c.setFillColor(C_PIECE_FILL)
    c.setStrokeColor(C_EDGE_BAND)
    c.setLineWidth(1.6)
    c.rect(x_m, top_y, w_m, SHELF_D, fill=1, stroke=1)

    # Canto trasero
    c.setFillColor(colors.HexColor("#E2E8F0"))
    c.setStrokeColor(C_PIECE_STROKE)
    c.setLineWidth(0.8)
    c.rect(x_m, canto_y, w_m, THICKNESS, fill=1, stroke=1)

    # Eje centro
    c.setStrokeColor(C_DRILL_CENTER)
    c.setLineWidth(0.4)
    c.setDash([3, 2])
    c.line(x_m - 4, canto_y + THICKNESS / 2, x_m + w_m + 4, canto_y + THICKNESS / 2)
    c.setDash([])

    # Barrenos Mediana: a 60 mm de orillas, 280 mm entre centros
    m_h1 = x_m + 60 * SCALE
    m_h2 = x_m + 340 * SCALE

    for hx in [m_h1, m_h2]:
        c.setFillColor(C_DRILL_FILL)
        c.setStrokeColor(C_DIM_LINE)
        c.setLineWidth(0.6)
        c.circle(hx, canto_y + THICKNESS / 2, dr, fill=1, stroke=1)

        c.setDash([2, 2])
        c.rect(hx - dr, top_y, 2 * dr, 105 * SCALE, fill=0, stroke=1)
        c.setDash([])

    # Cotas Mediana
    draw_dim_h(c, x_m, x_m + w_m, top_y + SHELF_D, "400 mm", offset=8)
    draw_dim_h(c, x_m, m_h1, canto_y, "60", offset=-11, text_above=False)
    draw_dim_h(c, m_h1, m_h2, canto_y, "280 mm", offset=-11, text_above=False)
    draw_dim_h(c, m_h2, x_m + w_m, canto_y, "60", offset=-11, text_above=False)

    # -------------------------------------------------------------
    # 3. REPISA GRANDE (500 x 150 mm)
    # -------------------------------------------------------------
    x_g = 470
    w_g = 500 * SCALE  # 220 pt

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(C_TEXT_MAIN)
    c.drawString(x_g, top_y + SHELF_D + 20, "PIEZA 3: GRANDE (500 x 150 mm)")

    # Planta
    c.setFillColor(C_PIECE_FILL)
    c.setStrokeColor(C_EDGE_BAND)
    c.setLineWidth(1.6)
    c.rect(x_g, top_y, w_g, SHELF_D, fill=1, stroke=1)

    # Canto trasero
    c.setFillColor(colors.HexColor("#E2E8F0"))
    c.setStrokeColor(C_PIECE_STROKE)
    c.setLineWidth(0.8)
    c.rect(x_g, canto_y, w_g, THICKNESS, fill=1, stroke=1)

    # Eje centro
    c.setStrokeColor(C_DRILL_CENTER)
    c.setLineWidth(0.4)
    c.setDash([3, 2])
    c.line(x_g - 4, canto_y + THICKNESS / 2, x_g + w_g + 4, canto_y + THICKNESS / 2)
    c.setDash([])

    # Barrenos Grande: a 75 mm de orillas, 350 mm entre centros
    g_h1 = x_g + 75 * SCALE
    g_h2 = x_g + 425 * SCALE

    for hx in [g_h1, g_h2]:
        c.setFillColor(C_DRILL_FILL)
        c.setStrokeColor(C_DIM_LINE)
        c.setLineWidth(0.6)
        c.circle(hx, canto_y + THICKNESS / 2, dr, fill=1, stroke=1)

        c.setDash([2, 2])
        c.rect(hx - dr, top_y, 2 * dr, 105 * SCALE, fill=0, stroke=1)
        c.setDash([])

    # Cotas Grande
    draw_dim_h(c, x_g, x_g + w_g, top_y + SHELF_D, "500 mm", offset=8)
    draw_dim_h(c, x_g, g_h1, canto_y, "75", offset=-11, text_above=False)
    draw_dim_h(c, g_h1, g_h2, canto_y, "350 mm", offset=-11, text_above=False)
    draw_dim_h(c, g_h2, x_g + w_g, canto_y, "75", offset=-11, text_above=False)

    # -------------------------------------------------------------
    # SECCIÓN INFERIOR IZQUIERDA: DETALLE D-01 (SECCIÓN BARRENO CORTE A-A)
    # -------------------------------------------------------------
    det_x = 45
    det_y = 110
    det_w = 340
    det_h = 195

    c.setFillColor(colors.white)
    c.setStrokeColor(C_BORDER_FRAME)
    c.setLineWidth(0.8)
    c.rect(det_x, det_y, det_w, det_h, fill=1, stroke=1)

    c.setFillColor(C_TITLE_BG)
    c.rect(det_x, det_y + det_h - 16, det_w, 16, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(det_x + 8, det_y + det_h - 11, "DETALLE D-01: CORTE A-A (SECCIÓN TRANSVERSAL DEL BARRENO)")

    # Dibujo de corte
    d_x = det_x + 35
    d_y = det_y + 60
    d_w = 190
    d_t = 65

    c.setFillColor(C_PIECE_FILL)
    c.setStrokeColor(C_BORDER_FRAME)
    c.setLineWidth(1.0)
    c.rect(d_x, d_y, d_w, d_t, fill=1, stroke=1)

    # Canto frontal con cubrecanto
    c.setStrokeColor(C_EDGE_BAND)
    c.setLineWidth(2.5)
    c.line(d_x + d_w, d_y, d_x + d_w, d_y + d_t)

    # Cavidad del barreno (105 mm x 10 mm)
    h_len = 130
    h_diam = 32
    h_y = d_y + (d_t - h_diam) / 2

    c.setFillColor(C_DRILL_FILL)
    c.setStrokeColor(C_DIM_LINE)
    c.setLineWidth(0.8)
    c.rect(d_x, h_y, h_len, h_diam, fill=1, stroke=1)

    # Punta cónica
    p_cone = c.beginPath()
    p_cone.moveTo(d_x + h_len, h_y)
    p_cone.lineTo(d_x + h_len + 10, h_y + h_diam / 2)
    p_cone.lineTo(d_x + h_len, h_y + h_diam)
    p_cone.close()
    c.drawPath(p_cone, fill=1, stroke=1)

    # Eje centro
    c.setStrokeColor(C_DRILL_CENTER)
    c.setLineWidth(0.5)
    c.setDash([4, 2])
    c.line(d_x - 10, d_y + d_t / 2, d_x + h_len + 20, d_y + d_t / 2)
    c.setDash([])

    # Cotas del detalle
    draw_dim_h(c, d_x, d_x + h_len, h_y, "Profundidad: 105 mm", offset=-13, text_above=False)
    draw_dim_v(c, d_x + h_len, h_y, h_y + h_diam, "Ø 10.0 mm", offset=20)
    draw_dim_v(c, d_x - 4, d_y, d_y + d_t / 2, "8 mm", offset=-8, text_right=False)
    draw_dim_v(c, d_x - 4, d_y + d_t / 2, d_y + d_t, "8 mm", offset=-8, text_right=False)

    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(C_TEXT_MAIN)
    c.drawString(det_x + 12, det_y + 25, "• Profundidad neta requerida para alojar vástago de 100 mm sin topar.")
    c.drawString(det_x + 12, det_y + 13, "• Centrado obligatorio a 8.0 mm para evitar reventar las caras.")

    # -------------------------------------------------------------
    # SECCIÓN INFERIOR DERECHA: NORMAS DE MAQUILA
    # -------------------------------------------------------------
    not_x = 405
    not_y = 110
    not_w = PAGE_W - 24 - 3 - not_x
    not_h = 195

    c.setFillColor(colors.white)
    c.setStrokeColor(C_BORDER_FRAME)
    c.setLineWidth(0.8)
    c.rect(not_x, not_y, not_w, not_h, fill=1, stroke=1)

    c.setFillColor(C_TITLE_BG)
    c.rect(not_x, not_y + not_h - 16, not_w, 16, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(not_x + 8, not_y + not_h - 11, "NORMAS TÉCNICAS OBLIGATORIAS PARA EL TALLER")

    specs = [
        "1. BROCA: Utilizar broca para madera punta espada/centradora Ø 10.0 mm.",
        "2. PERPENDICULARIDAD: Barrenar con taladro de banco o guía escuadra a 90°.",
        "   Desviación angular máxima admisible: 0.3°.",
        "3. EJE OBLIGATORIO: El barreno debe situarse a 8.0 mm exactos de la cara.",
        "4. CUBRECANTO: PVC blanco 19x0.45 mm aplicado en los 4 lados.",
        "   Refilado a ras sin rayar ni degollar la superficie de melamina.",
        "5. LIMPIEZA: Sopletear viruta residual de cada orificio antes de empacar.",
    ]
    c.setFillColor(C_TEXT_MAIN)
    c.setFont("Helvetica", 6.8)
    sy = not_y + not_h - 30
    for s in specs:
        c.drawString(not_x + 8, sy, s)
        sy -= 12


def page_2_nesting(c):
    """Página 2: Plano de corte y optimización del tablero (Nesting industrial)."""
    draw_title_block(c, 2, 3, "MAPA DE CORTE (NESTING)", "Escala 1:6")

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(C_TEXT_MAIN)
    c.drawString(36, 562, "PLANO 02: MAPA DE CORTE Y RENDIMIENTO DE TABLERO (1.22 x 2.44 m)")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(C_TEXT_MUTED)
    c.drawString(36, 550, "Rendimiento comprobado: 15 Sets completos (45 repisas individuales) por tablero comercial. Merma menor al 2.5%.")

    # Geometría del tablero:
    # Largo X = 2440 mm, Ancho Y = 1220 mm
    # A escala en pantalla: Largo X = 480 pt (scale = 480 / 2440 = 0.1967 pt/mm)
    # Altura Y = 1220 * 0.1967 = 240 pt
    SCALE_N = 0.1967
    bx = 45
    by = 265
    bw = 2440 * SCALE_N  # 480 pt
    bh = 1220 * SCALE_N  # 240 pt

    # Fondo tablero
    c.setFillColor(colors.HexColor("#FFFFFF"))
    c.setStrokeColor(C_BORDER_FRAME)
    c.setLineWidth(1.2)
    c.rect(bx, by, bw, bh, fill=1, stroke=1)

    # 15 tiras verticales de 150 mm
    # En Y (altura 1220 mm):
    # - Grande: 500 mm (y_g = 500 * SCALE_N = 98.35 pt)
    # - Mediana: 400 mm (y_m = 400 * SCALE_N = 78.68 pt)
    # - Chica: 300 mm (y_c = 300 * SCALE_N = 59.01 pt)
    # - Merma desorille superior: 20 mm (3.9 pt)
    y_g = 500 * SCALE_N
    y_m = 400 * SCALE_N
    y_c = 300 * SCALE_N
    strip_w = 150 * SCALE_N  # 29.5 pt

    col_g = colors.HexColor("#93C5FD")  # Azul 500 mm
    col_m = colors.HexColor("#86EFAC")  # Verde 400 mm
    col_c = colors.HexColor("#FDBA74")  # Naranja 300 mm
    col_w = colors.HexColor("#CBD5E1")  # Gris merma

    for i in range(15):
        sx = bx + i * strip_w

        # Grande (abajo)
        c.setFillColor(col_g)
        c.setStrokeColor(C_BORDER_FRAME)
        c.setLineWidth(0.4)
        c.rect(sx, by, strip_w, y_g, fill=1, stroke=1)

        # Mediana (centro)
        c.setFillColor(col_m)
        c.rect(sx, by + y_g, strip_w, y_m, fill=1, stroke=1)

        # Chica (arriba)
        c.setFillColor(col_c)
        c.rect(sx, by + y_g + y_m, strip_w, y_c, fill=1, stroke=1)

        # Merma superior
        c.setFillColor(col_w)
        c.rect(sx, by + y_g + y_m + y_c, strip_w, bh - (y_g + y_m + y_c), fill=1, stroke=1)

        # Etiqueta vertical en cada tira
        c.setFillColor(C_TEXT_MAIN)
        c.setFont("Helvetica-Bold", 5)
        c.drawCentredString(sx + strip_w / 2, by + 10, f"S{i+1}")
        c.drawCentredString(sx + strip_w / 2, by + y_g + 10, f"S{i+1}")
        c.drawCentredString(sx + strip_w / 2, by + y_g + y_m + 10, f"S{i+1}")

    # Retazo lateral derecho restante del tablero (2440 - 15*150 = 190 mm)
    scrap_w = bw - 15 * strip_w
    c.setFillColor(col_w)
    c.setStrokeColor(C_BORDER_FRAME)
    c.setLineWidth(0.4)
    c.rect(bx + 15 * strip_w, by, scrap_w, bh, fill=1, stroke=1)
    c.setFillColor(C_TEXT_MUTED)
    c.setFont("Helvetica-Bold", 6)
    c.saveState()
    c.translate(bx + 15 * strip_w + scrap_w / 2, by + bh / 2)
    c.rotate(90)
    c.drawCentredString(0, 0, "MERMA LATERAL (190 mm)")
    c.restoreState()

    # Cotas del tablero general
    draw_dim_h(c, bx, bx + bw, by + bh, "2440 mm (Largo Tablero)", offset=10)
    draw_dim_v(c, bx, by, by + bh, "1220 mm (Ancho)", offset=-10, text_right=False)

    # Cotas de las alturas de repisas
    draw_dim_v(c, bx + bw + 4, by, by + y_g, "500 mm (Grande)", offset=10)
    draw_dim_v(c, bx + bw + 4, by + y_g, by + y_g + y_m, "400 mm (Mediana)", offset=10)
    draw_dim_v(c, bx + bw + 4, by + y_g + y_m, by + y_g + y_m + y_c, "300 mm (Chica)", offset=10)

    # Cota de ancho de tira
    draw_dim_h(c, bx, bx + strip_w, by, "150 mm", offset=-10, text_above=False)

    # -------------------------------------------------------------
    # CUADRO LATERAL DERECHO: LEYENDA Y RENDIMIENTO
    # -------------------------------------------------------------
    lx = bx + bw + 60
    ly = by + 75
    lw = PAGE_W - 24 - 3 - lx
    lh = 165

    c.setFillColor(colors.white)
    c.setStrokeColor(C_BORDER_FRAME)
    c.setLineWidth(0.8)
    c.rect(lx, ly, lw, lh, fill=1, stroke=1)

    c.setFillColor(C_TITLE_BG)
    c.rect(lx, ly + lh - 16, lw, 16, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(lx + 8, ly + lh - 11, "RESUMEN DE RENDIMIENTO INDUSTRIAL")

    # Muestras de color
    legend_items = [
        (col_g, "Repisa Grande (500 x 150 mm)", "15 piezas"),
        (col_m, "Repisa Mediana (400 x 150 mm)", "15 piezas"),
        (col_c, "Repisa Chica (300 x 150 mm)", "15 piezas"),
        (col_w, "Mermas / Cortes de sierra", "< 2.5 %"),
    ]
    cur_y = ly + lh - 32
    for col, name, qty in legend_items:
        c.setFillColor(col)
        c.setStrokeColor(C_BORDER_FRAME)
        c.setLineWidth(0.5)
        c.rect(lx + 10, cur_y, 12, 10, fill=1, stroke=1)
        c.setFillColor(C_TEXT_MAIN)
        c.setFont("Helvetica-Bold", 6.8)
        c.drawString(lx + 26, cur_y + 2, name)
        c.drawRightString(lx + lw - 10, cur_y + 2, qty)
        cur_y -= 14

    c.setStrokeColor(colors.HexColor("#E2E8F0"))
    c.setLineWidth(0.5)
    c.line(lx + 8, cur_y + 4, lx + lw - 8, cur_y + 4)

    c.setFillColor(colors.HexColor("#065F46"))
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(lx + 8, cur_y - 8, "TOTAL: 15 SETS (45 REPISAS)")
    c.setFont("Helvetica", 6.8)
    c.setFillColor(C_TEXT_MAIN)
    c.drawString(lx + 8, cur_y - 20, "Costo madera por set: $46.00 MXN")
    c.drawString(lx + 8, cur_y - 30, "Aprovechamiento de área: 90.7 % útil neto")

    # -------------------------------------------------------------
    # SECCIÓN INFERIOR: SECUENCIA DE CORTE (OPERADOR DE SECCIONADORA)
    # -------------------------------------------------------------
    seq_x = 45
    seq_y = 110
    seq_w = bw  # Exactamente el ancho del tablero de arriba (480 pt)
    seq_h = 135

    c.setFillColor(colors.white)
    c.setStrokeColor(C_BORDER_FRAME)
    c.setLineWidth(0.8)
    c.rect(seq_x, seq_y, seq_w, seq_h, fill=1, stroke=1)

    c.setFillColor(C_TITLE_BG)
    c.rect(seq_x, seq_y + seq_h - 16, seq_w, 16, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(seq_x + 8, seq_y + seq_h - 11, "SECUENCIA DE CORTE RECOMENDADA EN ESCUADRADORA / SECCIONADORA")

    proc = [
        "PASO 1: DESORILLE PERIMETRAL",
        "  • Retirar 10 mm en el canto de 2440 mm y 10 mm en el de 1220 mm para sanear el tablero.",
        "PASO 2: CORTE LONGITUDINAL (15 TIRAS)",
        "  • Ajustar tope paralelo a 150.0 mm. Cortar 15 tiras continuas de 1220 mm de largo.",
        "  • Utilizar disco con incisor activo para evitar despostillado en la cara inferior de melamina.",
        "PASO 3: CORTE TRANSVERSAL EN PAQUETE",
        "  • Apilar 3 o 5 tiras en la mesa de escuadrar con prensa neumática.",
        "  • Corte 1: Tope a 500 mm (Repisa Grande). Corte 2: Tope a 400 mm (Repisa Mediana).",
        "  • El remanente automático es de 300 mm exactos (Repisa Chica).",
    ]
    c.setFillColor(C_TEXT_MAIN)
    py = seq_y + seq_h - 28
    for line in proc:
        if line.startswith("PASO"):
            c.setFont("Helvetica-Bold", 7)
        else:
            c.setFont("Helvetica", 6.8)
        c.drawString(seq_x + 8, py, line)
        py -= 11.5


def page_3_assembly_packaging(c):
    """Página 3: Ficha de herrajes, empaque comercial y control de calidad."""
    draw_title_block(c, 3, 3, "HERRAJES, EMPAQUE Y QA", "Especificación")

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(C_TEXT_MAIN)
    c.drawString(36, 562, "PLANO 03: KIT DE INSTALACIÓN, EMPAQUE Y CHECKLIST DE CONTROL DE CALIDAD")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(C_TEXT_MUTED)
    c.drawString(36, 550, "Estándar de entrega directa para bodegas Mercado Envíos Full. Cero rechazos por empaque o falta de componentes.")

    # -------------------------------------------------------------
    # 1. ESQUEMA DEL HERRAJE (PERNO INVISIBLE)
    # -------------------------------------------------------------
    bx1 = 45
    by1 = 330
    bw1 = 335
    bh1 = 205

    c.setFillColor(colors.white)
    c.setStrokeColor(C_BORDER_FRAME)
    c.setLineWidth(0.8)
    c.rect(bx1, by1, bw1, bh1, fill=1, stroke=1)

    c.setFillColor(C_TITLE_BG)
    c.rect(bx1, by1 + bh1 - 16, bw1, 16, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(bx1 + 8, by1 + bh1 - 11, "KIT DE ANCLAJE: PERNO INVISIBLE DE ACERO 10 x 100 mm")

    # Dibujo muro + taquete + perno + repisa
    px = bx1 + 30
    py = by1 + 105

    # Muro
    c.setFillColor(colors.HexColor("#CBD5E1"))
    c.setStrokeColor(C_BORDER_FRAME)
    c.setLineWidth(0.8)
    c.rect(px, py - 40, 50, 85, fill=1, stroke=1)
    c.setFillColor(C_TEXT_MAIN)
    c.setFont("Helvetica-Bold", 6.5)
    c.drawString(px + 6, py + 36, "MURO CONCRETO")

    # Taquete expansión nylon
    c.setLineWidth(0.6)
    c.setFillColor(colors.HexColor("#38BDF8"))
    c.rect(px + 8, py - 8, 42, 16, fill=1, stroke=1)

    # Perno de acero
    c.setFillColor(colors.HexColor("#94A3B8"))
    c.rect(px + 18, py - 5, 140, 10, fill=1, stroke=1)
    # Rosca central
    c.setFillColor(colors.HexColor("#64748B"))
    c.rect(px + 15, py - 7, 20, 14, fill=1, stroke=1)

    # Repisa embonando
    c.setFillColor(C_PIECE_FILL)
    c.setStrokeColor(C_BORDER_FRAME)
    c.setLineWidth(1.0)
    c.rect(px + 50, py - 25, 185, 50, fill=1, stroke=1)
    c.setFillColor(C_TEXT_MAIN)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(px + 120, py + 12, "REPISA FLOTANTE")

    # Cota vástago
    draw_dim_h(c, px + 50, px + 50 + 105, py - 25, "100 mm vástago interior", offset=-11, text_above=False)

    spec_txt = [
        "COMPONENTES REQUERIDOS POR SET (BOLSA SELLADA):",
        "• 6 Pernos de acero galvanizado Ø 10 mm x 100 mm (capacidad: 15 kg/par).",
        "• 6 Taquetes de expansión de nylon Ø 12 mm x 60 mm.",
        "• 1 Hoja de instructivo ilustrado con plantilla de barrenado para muro.",
    ]
    c.setFillColor(C_TEXT_MAIN)
    c.setFont("Helvetica", 6.8)
    ty = by1 + 45
    for l in spec_txt:
        c.drawString(bx1 + 10, ty, l)
        ty -= 11

    # -------------------------------------------------------------
    # 2. ESQUEMA DE EMPAQUE PARA MERCADO ENVÍOS FULL
    # -------------------------------------------------------------
    bx2 = 395
    by2 = 330
    bw2 = PAGE_W - 24 - 3 - bx2
    bh2 = 205

    c.setFillColor(colors.white)
    c.setStrokeColor(C_BORDER_FRAME)
    c.setLineWidth(0.8)
    c.rect(bx2, by2, bw2, bh2, fill=1, stroke=1)

    c.setFillColor(C_TITLE_BG)
    c.rect(bx2, by2 + bh2 - 16, bw2, 16, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(bx2 + 8, by2 + bh2 - 11, "ESPECIFICACIÓN DE EMPAQUE (CAJA 520 x 160 x 60 mm)")

    # Dibujo de caja
    cx = bx2 + 30
    cy = by2 + 75
    box_w = 265
    box_h = 75

    c.setFillColor(colors.HexColor("#FEF3C7"))
    c.setStrokeColor(colors.HexColor("#B45309"))
    c.setLineWidth(1.0)
    c.rect(cx, cy, box_w, box_h, fill=1, stroke=1)

    # Estiba de repisas
    c.setLineWidth(0.4)
    # Grande abajo (500)
    c.setFillColor(colors.HexColor("#93C5FD"))
    c.rect(cx + 10, cy + 8, 245, 14, fill=1, stroke=1)
    # Mediana en medio (400)
    c.setFillColor(colors.HexColor("#86EFAC"))
    c.rect(cx + 10, cy + 24, 196, 14, fill=1, stroke=1)
    # Chica arriba (300)
    c.setFillColor(colors.HexColor("#FDBA74"))
    c.rect(cx + 10, cy + 40, 147, 14, fill=1, stroke=1)

    # Bolsa herrajes en espacio libre superior
    c.setFillColor(colors.HexColor("#E0E7FF"))
    c.rect(cx + 165, cy + 30, 88, 24, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#3730A3"))
    c.setFont("Helvetica-Bold", 6.5)
    c.drawString(cx + 175, cy + 40, "BOLSA HERRAJES")

    draw_dim_h(c, cx, cx + box_w, cy + box_h, "520 mm Largo Interior", offset=7)
    draw_dim_v(c, cx + box_w, cy, cy + box_h, "60 mm", offset=7)

    pack_notes = [
        "REQUISITOS OBLIGATORIOS DE EMPAQUE PARA FULL:",
        "1. Cartón corrugado kraft 23 a 32 ECT (resiste 25 kg de estiba en tarima).",
        "2. Colocar poliburbuja o foam de 1 mm entre repisas para evitar rayaduras.",
        "3. Etiqueta térmica de código de barras ML visible en cara plana superior.",
    ]
    c.setFillColor(C_TEXT_MAIN)
    c.setFont("Helvetica", 6.8)
    ty = by2 + 45
    for l in pack_notes:
        c.drawString(bx2 + 10, ty, l)
        ty -= 11

    # -------------------------------------------------------------
    # 3. CHECKLIST DE CONTROL DE CALIDAD (QA)
    # -------------------------------------------------------------
    bx3 = 45
    by3 = 110
    bw3 = PAGE_W - 24 - 3 - bx3  # Ancho completo (696 pt)
    bh3 = 205

    c.setFillColor(colors.white)
    c.setStrokeColor(C_BORDER_FRAME)
    c.setLineWidth(0.8)
    c.rect(bx3, by3, bw3, bh3, fill=1, stroke=1)

    c.setFillColor(C_TITLE_BG)
    c.rect(bx3, by3 + bh3 - 16, bw3, 16, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(bx3 + 8, by3 + bh3 - 11, "CHECKLIST DE INSPECCIÓN EN TALLER (CRITERIOS OBLIGATORIOS PASA / NO PASA)")

    col1_items = [
        ("[  ] 1. Cero Despostillado:", "Aristas limpias sin saltaduras de melamina visibles."),
        ("[  ] 2. Adherencia de Canto:", "Cubrecanto sin despegues, bordes cortantes ni rebabas."),
        ("[  ] 3. Perpendicularidad:", "Insertar perno de prueba; debe quedar a 90° exactos a escuadra."),
        ("[  ] 4. Eje de Perforación:", "Revisar centro a 8.0 mm exactos. Desviación >1 mm = RECHAZO."),
    ]

    col2_items = [
        ("[  ] 5. Profundidad Barreno:", "El perno debe entrar libremente 100 mm sin topar viruta."),
        ("[  ] 6. Conteo de Herrajes:", "Bolsa sellada con exactamente 6 pernos y 6 taquetes."),
        ("[  ] 7. Protección Interna:", "Poliburbuja entre repisas para evitar fricción en flete."),
        ("[  ] 8. Etiquetado Full:", "Etiqueta térmica con código ML visible en cara plana superior."),
    ]

    c.setFillColor(C_TEXT_MAIN)
    qy1 = by3 + bh3 - 32
    for title, desc in col1_items:
        c.setFont("Helvetica-Bold", 6.8)
        c.drawString(bx3 + 12, qy1, title)
        c.setFont("Helvetica", 6.8)
        c.drawString(bx3 + 125, qy1, desc)
        qy1 -= 16

    qy2 = by3 + bh3 - 32
    for title, desc in col2_items:
        c.setFont("Helvetica-Bold", 6.8)
        c.drawString(bx3 + 360, qy2, title)
        c.setFont("Helvetica", 6.8)
        c.drawString(bx3 + 475, qy2, desc)
        qy2 -= 16


def build_pdf():
    os.makedirs(os.path.dirname(PDF_PATH), exist_ok=True)
    c = canvas.Canvas(PDF_PATH, pagesize=(PAGE_W, PAGE_H))

    # Página 1: Despiece y barrenado
    page_1_pieces(c)
    c.showPage()

    # Página 2: Mapa de corte y nesting
    page_2_nesting(c)
    c.showPage()

    # Página 3: Herrajes, empaque y QA
    page_3_assembly_packaging(c)
    c.showPage()

    c.save()
    print(f"Planos técnicos generados exitosamente en: {PDF_PATH}")


if __name__ == "__main__":
    build_pdf()
