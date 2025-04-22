from io import BytesIO
import weasyprint
from celery import shared_task
from django.contrib.staticfiles import finders
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from orders.models import Order
from django.conf import settings

@shared_task
def payment_completed(order_id):
    """
    Task ot send an e-mail notification when an order is successfully paid
    """
    order = Order.objects.get(id=order_id)
    # Create invoice e-mail
    subject = f'My Shop - Invoice no. {order.id}'
    message = ('Please, find attached the invoice for your recent purchase.')
    email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [order.email])
    # Generate PDF
    html = render_to_string('orders/order/pdf.html', {'order': order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(finders.find('css/pdf.css'))]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)
    # Attach PDF file
    email.attach(f'order_{order.id}.pdf', out.getvalue(), 'application/pdf')
    # Send e-mail
    email.send()