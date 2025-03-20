from django.dispatch import receiver
from django.shortcuts import get_object_or_404

from paypal.standard.ipn.signals import valid_ipn_received
from allauth.account.signals import user_logged_in

from .models import Transaction
from .shop_utils import merge_carts, merge_wishlists

@receiver(valid_ipn_received)
def paypal_ipn_handler(sender, **kwargs):
    ipn = sender
    if ipn.payment_status == 'Completed':
        transaction = get_object_or_404(Transaction, id=ipn.invoice)
        if transaction.total_price == ipn.mc_gross:
            transaction.status = 'paid'
            transaction.save()

@receiver(user_logged_in)
def merge_user_data_on_login(request, user, **kwargs):
    merge_carts(request, user)
    merge_wishlists(request, user)