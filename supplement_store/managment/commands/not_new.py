from django.core.management.base import BaseCommand
from django.utils import timezone
from supplement_store.models import Item

class NotNew(BaseCommand):
    help = 'Mark items as not new after 14 days'

    def handle(self, *args, **options):
        today = timezone.now().date()
        cutoff_date = today - timezone.timedelta(days=14)

        # Update items that were created more than 14 days ago
        updated_items = Item.objects.filter(is_new=True, created_at__lt=cutoff_date).update(is_new=False)

        self.stdout.write(self.style.SUCCESS(f'{updated_items} items marked as not new.'))
