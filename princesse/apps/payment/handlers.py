from datetime import date, datetime
from payment.models import Payment
import logging

# Configuración básica de logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_handler = logging.FileHandler('/code/princesse/logs/change_status.log')
log_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)


def handle_update_status(date_sub=None):
    today = date.today() if not date_sub else datetime.strptime(date_sub, '%d-%m-%y').date()
    payments = Payment.objects.filter(status='RETIRADO' ,return_date__lt=today)
    updated_payment_ids = []

    for payment in payments:
        payment.status = 'VENCIDO'
        payment.save()
        updated_payment_ids.append(payment.payment_id)  # Guardamos el ID del pago actualizado
    
    # Registrar los IDs en el archivo de log
    if updated_payment_ids:
        logger.info(f'Pagos actualizados: {", ".join(map(str, updated_payment_ids))}')
    else:
        logger.info('No se actualizaron pagos.')