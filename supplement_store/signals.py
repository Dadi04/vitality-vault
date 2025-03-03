from django.dispatch import receiver
from django.shortcuts import get_object_or_404

from paypal.standard.ipn.signals import valid_ipn_received

from .models import Transaction

@receiver(valid_ipn_received)
def paypal_ipn_handler(sender, **kwargs):
    ipn = sender
    if ipn.payment_status == 'Completed':
        transaction = get_object_or_404(Transaction, id=ipn.invoice)
        if transaction.total_price == ipn.mc_gross:
            transaction.status = 'paid'
            transaction.save()