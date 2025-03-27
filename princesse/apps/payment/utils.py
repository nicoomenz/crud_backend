from reportlab.lib.pagesizes import letter, A3, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from io import BytesIO
import os.path

def generate_invoice_pdf(data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    logo_path = os.path.join(os.path.dirname('/home/nico/MyProjects/princesse/princesse_bd_backend/princesse/static/images/'), 'dress.jpeg')
    
    def check_page_overflow(y_position, threshold=50):
        """Check if the content exceeds the page and create a new page if necessary."""
        if y_position < threshold:
            c.showPage()  # Create a new page
            draw_header()  # Redraw the header on the new page
            return height - 100  # Reset y_position
        return y_position
    
    def draw_header():
        # Posición y tamaño del logo
        logo_width = 50
        logo_height = 50
        c.drawImage(logo_path, 40, height - 80, width=logo_width, height=logo_height, mask='auto')

        # Texto al lado del logo
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, height - 40, "Princesse")
        c.setFont("Helvetica", 12)
        c.drawString(100, height - 55, "El palacio de las novias")
        c.drawString(100, height - 70, "Alquiler y ventas")
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(100, height - 85, "de Mónica Renata Fernandez")

    draw_header()

    # 🏷️ Mini encabezados
    c.drawString(60, height - 120, "Orden")
    c.drawString(60, height - 130, f"#{data['payment_id']}")
    c.drawString(450, height - 120, "Fecha")
    c.drawString(450, height - 130, f"{data['payment_date']}")

    c.drawString(60, height - 160, "Cliente")
    c.drawString(60, height - 170, f"{data['client']['first_name']} {data['client']['last_name']}")
    c.drawString(60, height - 180, f"{data['client']['dni']}")
    c.drawString(60, height - 190, f"{data['client']['cuit']}")
    c.drawString(60, height - 190, f"{data['client']['direccion']}")
    c.drawString(450, height - 170, f"{data['client']['email']}")
    c.drawString(450, height - 180, f"{data['client']['phone']}")

    # 🚀 Header sombreado para productos
    header_y = height - 230
    row_height = 18

    # Fondo sombreado
    c.setFillColor(colors.lightgrey)
    c.rect(50, header_y, width - 110, row_height, fill=True, stroke=False)

    # Texto del header
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(60, header_y + 5, "Producto(s)")
    c.drawString(width - 110, header_y + 5, "Costo")

    y_position = 520
    c.setFont("Helvetica", 10)
    # Inicializar precio total de los productos
    total_productos = 0
    precio_unitario = 0
    precio_total_combo = 0
    for combo in data.get('combo', []):
        y_position = check_page_overflow(y_position)
        descripcion = f"{combo['marca']['nombre']} - {combo['color']['nombre']} - talle {combo['talle']['nombre']}"
        precio_unitario = float(combo['precio'].get(data['price_type'], 0))
        precio_total_combo = precio_unitario * combo['cantidad']
        c.drawString(500, y_position, f"${precio_total_combo}")
        c.drawString(60, y_position, f"Combo: {descripcion}")
        y_position -= 20
        for producto in combo['productos']:
            detalle = f"{producto['categoria']['nombre']} - {producto['marca']['nombre']} - {producto['color']['nombre']}"
            c.drawString(70, y_position, detalle)
            y_position -= 10
            c.drawString(70, y_position, f"cantidad: {combo['cantidad']}")
            y_position -= 10
        y_position -= 20
    y_position -= 20

    # Imprimir productos
    for producto in data['productos']:
        y_position = check_page_overflow(y_position)
        # Determinar si el producto tiene estructura detallada o es un CustomProduct
        if "categoria" in producto:
            descripcion = f"{producto['categoria']['nombre']} - {producto['marca']['nombre']} - {producto['talle']['nombre']}"
            precio_unitario = float(producto['precio'].get(data['price_type'], 0))
        else:
            descripcion = f"{producto['name']} - {producto['color']} - {producto['talle']}"
            precio_unitario = float(producto['precio'])

        precio_por_producto = precio_unitario * producto["cantidad"]

        c.drawString(60, y_position, descripcion)
        c.drawString(60, y_position-10, f"cantidad: {producto['cantidad']}")
        c.drawString(60, y_position-20, f"color: {producto['color']['nombre']}")
        c.drawString(500, y_position, f"${precio_por_producto}")

        total_productos += precio_por_producto
        y_position -= 20  # Espacio para el siguiente producto
    
    y_position = check_page_overflow(y_position)
    # Descripción
    description_y_position = y_position - 20  # Espacio después de los productos
    c.drawString(60, description_y_position, f"Detalles")
    c.drawString(60, description_y_position - 10, f"{data['description'] if data['description'] else 'Sin descripción'}")
    c.drawString(500, description_y_position, f"${data['detail_amount'] if data['detail_amount'] else 0}")
    y_position = check_page_overflow(y_position)
    # Detalles del pago (Precios finales)
    y_position -= 80
    c.drawString(60, y_position, f"Tipo de Pago")
    c.drawString(500, y_position, f"{data['price_type']}")
    y_position = check_page_overflow(y_position)
    y_position -= 20
    c.drawString(60, y_position, f"Seña")
    c.drawString(500, y_position, f"${data['small_amount']}")
    y_position = check_page_overflow(y_position)
    y_position -= 20
    c.drawString(60, y_position, f"Descuento")
    c.drawString(500, y_position, f"{data['descuento']}%")
    y_position = check_page_overflow(y_position)
    y_position -= 20
    c.drawString(60, y_position, f"Subtotal")
    c.drawString(500, y_position, f"${data['subtotal_amount']}")
    y_position = check_page_overflow(y_position)
    y_position -= 20
    c.drawString(60, y_position, f"Saldo restante")
    c.drawString(500, y_position, f"${float(float(data['total_amount']))}")
    y_position = check_page_overflow(y_position)
    # Detalles adicionales (fechas de retiro y devolución)
    y_position -= 30

    c.drawString(100, y_position - 20, f"Fecha de Retiro")
    c.drawString(100, y_position - 40, f"{data['pick_up_date']}")
    c.drawString(400, y_position - 20, f"Fecha de Devolución")
    c.drawString(400, y_position - 40, f"{data['return_date']}")
    y_position = check_page_overflow(y_position)
    # Agregar reglas al pie del PDF
    rules_y_position = y_position - 80
    rules_y_position = check_page_overflow(rules_y_position)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, rules_y_position, "Importante:")
    c.setFont("Helvetica", 10)
    rules_text = [
        "La devolución de las prendas se hará dentro de la fecha establecida y en las mismas condiciones en que se han entregado,",
        "de lo contrario se abonará la multa correspondiente:",
        "a) El total de la limpieza de las mismas.",
        "b) Por el deterioro de las prendas se abonará el valor de las mismas.",
        "c) Las prendas se deberán devolver el día indicado, de lo contrario abonará un recargo por día sobre el monto del alquiler."
    ]
    rules_y_position = check_page_overflow(rules_y_position)
    for rule in rules_text:
        c.drawString(30, rules_y_position - 20, rule)
        rules_y_position -= 15
        rules_y_position = check_page_overflow(rules_y_position)
    # Finaliza el PDF
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer


