from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from io import BytesIO


def generate_invoice_pdf(data):
    # Crear un buffer para el PDF
    buffer = BytesIO()
    
    # Crear el canvas de ReportLab
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Establecer fuentes
    c.setFont("Helvetica", 12)
    
    # Título de la factura - Centrado
    title = "Factura de Pago"
    c.setFont("Helvetica-Bold", 18)
    title_width = c.stringWidth(title, "Helvetica-Bold", 18)  # Obtener el ancho del título
    c.drawString((letter[0] - title_width) / 2, 750, title)  # Centrar el título
    
    # Detalles del pago (Encabezado)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 720, f"Factura #{data['payment_id']}")
    c.setFont("Helvetica", 12)
    c.drawString(400, 720, f"Fecha: {data['payment_date']}")

    # Espacio para el cliente
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 690, "Datos del Cliente:")
    c.setFont("Helvetica", 12)
    c.drawString(100, 670, f"Nombre: {data['client']['first_name']} {data['client']['last_name']}")
    c.drawString(100, 650, f"DNI: {data['client']['dni']}")
    c.drawString(100, 630, f"CUIT: {data['client']['cuit']}")
    c.drawString(100, 610, f"Dirección: {data['client']['direccion']}")
    c.drawString(100, 590, f"Email: {data['client']['email']}")
    c.drawString(100, 570, f"Teléfono: {data['client']['phone']}")
    c.drawString(100, 550, f"IVA: {data['client']['iva']}")

    # Línea de separación
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(100, 540, 500, 540)

    # Detalles de los productos
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 510, "Productos Facturados:")
    c.setFont("Helvetica", 12)
    
    # Crear encabezado de tabla
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 490, "Producto")
    c.drawString(300, 490, "Cantidad")
    c.drawString(400, 490, "Precio Unitario")
    c.drawString(500, 490, "Total")
    
    y_position = 470
    c.setFont("Helvetica", 12)

    # Inicializar precio total de los productos
    total_productos = 0

    # Imprimir productos
    for producto in data['productos']:
        precio_por_producto = float(producto['precio']['efectivo']) * producto['cantidad']
        c.drawString(100, y_position, f"{producto['categoria']['nombre']} - {producto['marca']['nombre']} - {producto['color']['nombre']}")
        c.drawString(300, y_position, f"{producto['cantidad']}")
        c.drawString(400, y_position, f"${producto['precio']['efectivo']}")
        c.drawString(500, y_position, f"${precio_por_producto}")
        total_productos += precio_por_producto  # Sumar el total de los productos
        y_position -= 20  # Espacio para el siguiente producto

    # Descripción
    description_y_position = y_position - 20  # Espacio después de los productos
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, description_y_position, f"Descripción:")
    c.setFont("Helvetica", 12)
    c.drawString(100, description_y_position - 20, f"{data['description']}")

    # Línea de separación
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(100, description_y_position - 40, 500, description_y_position - 40)

    # Detalles del pago (Precios finales)
    y_position = description_y_position - 60
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y_position, "Detalles del Pago:")
    c.setFont("Helvetica", 12)
    y_position -= 20
    c.drawString(100, y_position, f"Tipo de Pago: {data['price_type']}")
    
    # Precio por Producto
    y_position -= 20
    c.drawString(100, y_position, f"Precio por Producto: ${total_productos}")
    
    y_position -= 20
    c.drawString(100, y_position, f"Seña: ${data['small_amount']}")
    y_position -= 20
    c.drawString(100, y_position, f"Total por Detalles: ${data['detail_amount']}")
    y_position -= 20
    c.drawString(100, y_position, f"Descuento: {data['descuento']}%")
    y_position -= 20
    c.drawString(100, y_position, f"Subtotal: ${data['subtotal_amount']}")
    y_position -= 20
    c.drawString(100, y_position, f"Total a Pagar: ${data['total_amount']}")

    # Línea de separación
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(100, y_position - 10, 500, y_position - 10)

    # Detalles adicionales (fechas de retiro y devolución)
    y_position -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y_position, "Fechas:")
    c.setFont("Helvetica", 12)
    c.drawString(100, y_position - 20, f"Fecha de Retiro: {data['pick_up_date']}")
    c.drawString(100, y_position - 40, f"Fecha de Devolución: {data['return_date']}")

    # Agregar reglas al pie del PDF
    rules_y_position = y_position - 80
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

    for rule in rules_text:
        c.drawString(30, rules_y_position - 20, rule)
        rules_y_position -= 15

    # Cerrar el canvas y devolver el contenido en formato PDF
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer
