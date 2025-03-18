from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from supplement_store.models import Item
from supplement_store.models import Item
import os
import re
from django.conf import settings

class Command(BaseCommand):
    help = 'Mark items as not new after 30 days and remove sale after that sale ends'

    def handle(self, *args, **options):
        today = timezone.now().date()
        items = Item.objects.all()
        for item in items:
            if item.created_at:
                expiry_date = item.created_at.date() + timedelta(days=30)
                if today < expiry_date:
                    remaining_days = (expiry_date - today).days
                    self.stdout.write(
                        f'Item {item.id} will have "is_new" removed in {remaining_days} days'
                    )
                else:
                    if item.is_new:
                        item.is_new = False
                        self.stdout.write(
                            f'Item {item.id} status "new" is removed'
                        )
                        item.save(update_fields=['is_new'])

            if item.sale_start_date and item.sale_end_date:
                if today < item.sale_start_date:
                    self.stdout.write(f'Item {item.id} sale is scheduled to start on {item.sale_start_date}')
                elif item.sale_start_date <= today <= item.sale_end_date:
                    self.stdout.write(f'Item {item.id} is currently on sale')
                elif today > item.sale_end_date:
                    if item.sale_price is not None:
                        item.sale_price = None
                        item.sale_start_date = None
                        item.sale_end_date = None
                        self.stdout.write(f'Item {item.id} sale has ended and is removed')
                        item.save(update_fields=['sale_price', 'sale_start_date', 'sale_end_date'])