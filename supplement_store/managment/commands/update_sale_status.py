from django.core.management.base import BaseCommand
from django.utils import timezone
from supplement_store.models import Item

class UpdateSaleStatus(BaseCommand):
    help = 'Update sale status for expired items'

    def handle(self, *args, **options):
        today = timezone.now().date()
        expired_items = Item.objects.filter(sale_end_date__lt=today, is_on_sale=True)

        for item in expired_items:
            try:
                item.is_on_sale = False
                item.sale_end_date = None
                item.sale_start_date = None
                item.sale_price = None
                item.save()
            except Exception as e:
                print(e)

        self.stdout.write(self.style.SUCCESS(f'Sale status updated for {len(expired_items)} items.'))
