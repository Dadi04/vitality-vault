from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from supplement_store.models import Item

class Command(BaseCommand):
    help = 'Mark items as not new after 30 days and remove sale after that sale ends'

    def handle(self, *args, **options):
        today = timezone.now().date()
        items = Item.objects.all()
        for item in items:
            if item.created_at and today >= (item.created_at.date() + timedelta(days=30)):
                if item.is_new:
                    item.is_new = False
                    self.stdout.write(f'Item {item.id} status "new" is removed')
                    item.save(update_fields=['is_new'])

            if item.sale_start_date and item.sale_end_date:
                if not (item.sale_start_date <= today <= item.sale_end_date):
                    print(item)
                    if item.sale_price is not None:
                        item.sale_price = None
                        item.sale_start_date = None
                        item.sale_end_date = None
                        self.stdout.write(f'Item {item.id} sale is removed')
                        item.save(update_fields=['sale_price', 'sale_start_date', 'sale_end_date'])
