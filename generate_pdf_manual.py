import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_PATH = "/Users/dlpo.c./Desktop/MANUAL_DE_USO_MERCADO_LIBRE_RESEARCH.pdf"


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#71717A"))

        # Header on pages > 1
        if self._pageNumber > 1:
            self.drawString(54, 750, "PLATAFORMA DE RESEARCH — GUÍA DE OPERACIÓN & BÚSQUEDA")
            self.drawRightString(612 - 54, 750, "MERCADO LIBRE MÉXICO")
            self.setStrokeColor(colors.HexColor("#E4E4E7"))
            self.setLineWidth(0.5)
            self.line(54, 744, 612 - 54, 744)

        # Footer
        self.setStrokeColor(colors.HexColor("#E4E4E7"))
        self.setLineWidth(0.5)
        self.line(54, 45, 612 - 54, 45)
        self.drawString(54, 32, "Manual Operativo • Uso Interno Autorizado")
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(612 - 54, 32, page_str)
        self.restoreState()


def build_pdf():
    os.makedirs(os.path.dirname(PDF_PATH), exist_ok=True)
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Color Palette
    c_flame = colors.HexColor("#F65058")
    c_dark = colors.HexColor("#090A0F")
    c_border = colors.HexColor("#E4E4E7")
    c_bg_light = colors.HexColor("#FAFAFA")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_dark,
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=c_flame,
        spaceAfter=12,
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=c_dark,
        spaceBefore=11,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#18181B"),
        spaceAfter=5,
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=10,
        spaceAfter=3,
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#1F2937"),
    )

    table_header_style = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
    )

    table_cell_style = ParagraphStyle(
        'TC',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_dark,
    )

    code_style = ParagraphStyle(
        'Code',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0F172A"),
    )

    story = []

    # Title & Header
    badge_html = "GUÍA PRÁCTICA & OPERATIVA &nbsp;|&nbsp; MERCADO LIBRE MÉXICO"
    story.append(Paragraph(badge_html, subtitle_style))
    story.append(Paragraph("Manual de Operación de la Plataforma de Research", title_style))
    story.append(Paragraph("Búsqueda de Productos • Detección de Vacíos de Mercado • Simulador de Ganancias", ParagraphStyle('Desc', fontName='Helvetica', fontSize=9, textColor=colors.HexColor("#52525B"), spaceAfter=8)))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_flame, spaceBefore=0, spaceAfter=10))

    # Section 1: Acceso
    story.append(Paragraph("1. Acceso a la Plataforma", h1_style))
    story.append(Paragraph("Puedes ingresar a la herramienta desde cualquier computadora o teléfono móvil con internet:", body_style))

    cred_data = [
        [Paragraph("Dato de Acceso", table_header_style), Paragraph("Información para Ingresar", table_header_style), Paragraph("Notas Importantes", table_header_style)],
        [Paragraph("Enlace Web", table_cell_style), Paragraph("https://wrapped-thanksgiving-date-dolls.trycloudflare.com", code_style), Paragraph("Acceso directo seguro vía navegador.", table_cell_style)],
        [Paragraph("Usuario", table_cell_style), Paragraph("admin", code_style), Paragraph("Cuenta de acceso con privilegios completos.", table_cell_style)],
        [Paragraph("Contraseña", table_cell_style), Paragraph("Admin!Riviera2026", code_style), Paragraph("Respetar mayúsculas y caracteres especiales.", table_cell_style)],
        [Paragraph("Sesión Activa", table_cell_style), Paragraph("8 Horas continuas", table_cell_style), Paragraph("Tras 8h de inactividad, vuelve a iniciar sesión.", table_cell_style)],
    ]
    t_cred = Table(cred_data, colWidths=[100, 240, 164])
    t_cred.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_dark),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_cred)

    security_note = [
        [Paragraph("<b>⚠️ Aviso de Seguridad (Bloqueo Temporal):</b><br/>"
                   "Si se escribe la contraseña errónea <b>5 veces seguidas</b>, la pantalla se bloqueará por <b>60 segundos</b> como medida de protección. Verás un contador en pantalla; simplemente espera a que llegue a cero para volver a escribir la contraseña correcta.", callout_style)]
    ]
    t_sec = Table(security_note, colWidths=[504])
    t_sec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF3C7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#F59E0B")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(Spacer(1, 4))
    story.append(t_sec)
    story.append(Spacer(1, 8))

    # Section 2: Búsqueda
    story.append(Paragraph("2. Cómo Realizar una Búsqueda de Mercado", h1_style))
    story.append(Paragraph("• <b>Búsqueda Libre:</b> Escribe en la barra central el nombre de cualquier producto o categoría (ejemplo: <i>hamacas</i>, <i>miel melipona</i>, <i>copal</i>, <i>trajes de baño</i>, <i>café orgánico</i>).", bullet_style))
    story.append(Paragraph("• <b>Etiquetas Sugeridas:</b> Puedes hacer clic directamente en las píldoras ubicadas debajo de la barra para cargar de inmediato los nichos pre-configurados de la región.", bullet_style))
    story.append(Paragraph("• <b>Resultados en Vivo:</b> Al presionar <i>Enter</i> o el botón de búsqueda, la plataforma analiza los catálogos activos de Mercado Libre México en tiempo real.", bullet_style))
    story.append(Spacer(1, 8))

    # Section 3: Océanos Azules
    story.append(Paragraph("3. Cómo Interpretar los \"Océanos Azules\" (Vacíos de Oferta)", h1_style))
    story.append(Paragraph("En la parte superior de los resultados verás tarjetas destacadas llamadas <b>Océanos Azules</b>:", body_style))
    story.append(Paragraph("• <b>¿Qué significan?</b> Son rangos de precio donde la gente está comprando, pero <b>casi ningún vendedor ofrece un buen producto</b>. Representan oportunidades ideales para vender con buen margen.", bullet_style))
    story.append(Paragraph("• <b>Ejemplo Práctico:</b> Si la tarjeta dice <i>$650 a $950 MXN (Score 9.5/10)</i>, significa que los competidores venden o muy barato (baja calidad) o muy caro (importados), dejando ese rango intermedio libre para que nosotros entremos con un producto bien presentado sin competir por precio.", bullet_style))
    story.append(Paragraph("• <b>Puntuación de Oportunidad:</b> Entre más cercano a <b>10 / 10</b>, más rentable y desatendido está ese segmento.", bullet_style))
    story.append(Spacer(1, 8))

    # Section 4: Arquetipos
    story.append(Paragraph("4. Filtrar los Productos Clave (Arquetipos de Mercado)", h1_style))
    story.append(Paragraph("Al costado del contador de productos encontrarás el botón <b>\"Filtrar arquetipos\"</b>:", body_style))
    story.append(Paragraph("• <b>Función:</b> Limpia la lista y oculta publicaciones secundarias o repetidas.", bullet_style))
    story.append(Paragraph("• <b>Resultado:</b> Muestra únicamente los productos que definen el mercado (los más vendidos, los que marcan el precio de referencia o los que tienen mejor posicionamiento).", bullet_style))
    story.append(Paragraph("• Para volver a ver el catálogo completo, solo haz clic de nuevo sobre el botón.", bullet_style))
    story.append(Spacer(1, 8))

    # Section 5: Enlace Directo a Mercado Libre
    story.append(Paragraph("5. Ver el Producto Directamente en Mercado Libre", h1_style))
    story.append(Paragraph("• <b>Desde la Lista de Resultados:</b> Cada fila incluye un enlace que dice <b>\"Ver en ML ↗\"</b> para abrir el producto directamente en la tienda oficial en una pestaña nueva.", bullet_style))
    story.append(Paragraph("• <b>Desde la Ficha Detallada:</b> En el encabezado del producto encontrarás el botón coral <b>\"Ver publicación en Mercado Libre ↗\"</b> para revisar las fotos en alta resolución, preguntas de compradores y reputación del vendedor.", bullet_style))
    story.append(Spacer(1, 8))

    # Section 6: Calculadora de Ganancia
    story.append(Paragraph("6. Calculadora de Ganancia y Costos en Vivo (Unit Economics)", h1_style))
    story.append(Paragraph("Al hacer clic en cualquier producto de la tabla, entrarás a su ficha técnica con la calculadora en tiempo real:", body_style))

    calc_box = [
        [Paragraph("<b>CÓMO CALCULAR TU GANANCIA:</b><br/>"
                   "1. <b>Precio de Venta Sugerido ($ MXN):</b> Viene con el precio actual en Mercado Libre. Puedes cambiarlo libremente para probar distintos escenarios de venta.<br/>"
                   "2. <b>Costo de Compra ($ MXN):</b> Escribe lo que nos cuesta adquirir o fabricar una unidad con el proveedor.<br/>"
                   "3. <b>Comisión Mercado Libre:</b> El sistema descuenta automáticamente la comisión oficial (~17.5%).<br/>"
                   "4. <b>Resultados Automáticos:</b> Verás en verde tu <b>Margen Neto en pesos</b> y el <b>% de Ganancia</b> que te deja cada venta.", callout_style)]
    ]
    t_calc = Table(calc_box, colWidths=[504])
    t_calc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#ECFDF5")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#10B981")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_calc)
    story.append(Spacer(1, 8))

    # Section 7: Comparador
    story.append(Paragraph("7. Cómo Comparar Productos Frente a Frente", h1_style))
    story.append(Paragraph("1. Marca la casilla <b>\"Comparar\"</b> en dos o más artículos de la lista.", bullet_style))
    story.append(Paragraph("2. Haz clic en el botón superior <b>\"Comparar X productos\"</b>.", bullet_style))
    story.append(Paragraph("3. Se abrirá una tabla comparativa donde verás lado a lado: precios, ventas estimadas al mes, nivel de demanda, nivel de competencia y tendencia histórica.", bullet_style))
    story.append(Spacer(1, 8))

    # Section 8: Guardar y Exportar Reportes
    story.append(Paragraph("8. Guardar Análisis y Descargar Reportes", h1_style))
    story.append(Paragraph("• <b>Guardar Estudio:</b> Tras realizar una búsqueda, haz clic en <b>\"Guardar análisis\"</b> y ponle un nombre claro (ejemplo: <i>Hamacas Mayas — Octubre 2026</i>).", bullet_style))
    story.append(Paragraph("• <b>Consultar Guardados:</b> En el menú superior haz clic en <b>\"REPORTES\"</b> para ver todo el historial.", bullet_style))
    story.append(Paragraph("• <b>Exportar a Excel (CSV):</b> Haz clic en el botón <b>CSV</b> para descargar los datos numéricos y abrirlos en Excel o Google Sheets.", bullet_style))
    story.append(Paragraph("• <b>Exportar a PDF:</b> Haz clic en el botón <b>PDF</b> para descargar un resumen formal listo para imprimir o enviar.", bullet_style))
    story.append(Spacer(1, 8))

    # Section 9: Salir
    story.append(Paragraph("9. Cierre de Sesión Seguro", h1_style))
    story.append(Paragraph("Al terminar tus actividades, haz clic en el botón <b>\"Salir\"</b> en la esquina superior derecha junto a tu nombre de usuario para cerrar tu sesión.", body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully updated at: {PDF_PATH}")


if __name__ == "__main__":
    build_pdf()
