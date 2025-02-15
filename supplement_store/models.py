from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from decimal import Decimal

from .countries import COUNTRIES

# Create your models here.

def item_image_upload_path(instance, filename):
    return f'supplement_store/static/supplement_store/images/product_images/{instance.fullname}/{instance.id}_{filename}'

def slide_show_upload_path(instance, filename):
    return f'supplement_store/static/supplement_store/images/slide_show_images/{timezone.now().strftime("%Y-%m-%d_%H-%M-%S")}_{filename}'

# napriti da se is new skida nakon 1 meseca
# napraviti da se sale stavi na sale start date i da se skine na sale end date

class User(AbstractUser):
    is_support = models.BooleanField(default=False)
    remember_me = models.BooleanField(default=True)
    address = models.CharField(default=None)
    city = models.CharField(default=None)
    state = models.CharField(null=True, blank=True, default=None)
    country = models.TextField(choices=COUNTRIES.items())
    zipcode = models.CharField(default=None)
    phone = models.CharField(default=None)
    birth = models.DateField(default='1900-01-01')

class Item(models.Model):
    CATEGORIES = (
        ('Protein powders','Protein powders'),
        ('Creatine','Creatine'),
        ('Pre-Workouts','Pre-Workouts'),
        ('Post-Workouts','Post-Workouts'),
        ('Amino Acids','Amino Acids'),
        ('Test Boosters','Test Boosters'),
        ('Mass Gainers', 'Mass Gainers'),
        ('Weight Loss', 'Weight Loss'),
        ('Vitamins and Minerals','Vitamins and Minerals'),
        ('Meal Replacements','Meal Replacements'),
        ('Clothing','Clothing'),
        ('Workout Accessories','Workout Accessories'),
    )
    BRANDS = (
        ('IronMaxx','IronMaxx'),
        ('OstroVit','OstroVit'),
        ('BioTechUSA','BioTechUSA'),
        ('AmiX','AmiX'),
        ('Myprotein','Myprotein'),
        ('BSN','BSN'),
        ('Optinum Nutrition','Optinum Nutrition'),
        ('Scitec Nutrition','Scitec Nutrition'),
        ('Gorilla Mind','Gorilla Mind'),
        ('HTLT','HTLT'),
        ('Quest Nutrition','Quest Nutrition'),
        ('Gymshark','Gymshark'),
        ('Under Armour','Under Armour'),
        ('Retaliation Project','Retaliation Project'),
    )

    name = models.CharField(max_length=40)
    fullname = models.CharField(max_length=60)
    category = models.CharField(choices=CATEGORIES)
    subcategory = models.CharField(max_length=50)
    brand = models.CharField(choices=BRANDS)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    average_rating = models.FloatField(default=0, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    quantity = models.PositiveIntegerField(default=20)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_start_date = models.DateField(null=True, blank=True)
    sale_end_date = models.DateField(null=True, blank=True)
    weight = models.PositiveIntegerField(null=True, blank=True)
    flavor = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=5, null=True, blank=True)
    size = models.CharField(max_length=3, null=True, blank=True)
    color = models.CharField(max_length=10, null=True, blank=True)
    is_new = models.BooleanField(default=True)
    popularity = models.IntegerField(default=0)
    main_image = models.ImageField(upload_to=item_image_upload_path, max_length=255)
    image1 = models.ImageField(upload_to=item_image_upload_path, blank=True, null=True, max_length=255)
    image2 = models.ImageField(upload_to=item_image_upload_path, blank=True, null=True, max_length=255)
    image3 = models.ImageField(upload_to=item_image_upload_path, blank=True, null=True, max_length=255)

    def serialize(self):
        return {
            'id': self.id,
            'fullname': self.fullname,
            'flavor': self.flavor,
            'price': self.price,
            'main_image': str(self.main_image.name),
            'image1': str(self.image1),
            'image2': str(self.image2),
            'is_new': self.is_new,
            'is_available': self.is_available,
            'sale_price': float(self.sale_price) if self.sale_price else '',
            'sale_start_date': self.sale_start_date,
            'sale_end_date': self.sale_end_date,
            'quantity': self.quantity,
        }

    def __str__(self):
        return f'{self.id}: {self.fullname}, Available: {self.is_available}'

# class Sale(models.Model):
#     item = models.ForeignKey(Item, on_delete=models.CASCADE)
#     sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     sale_start_date = models.DateField(null=True, blank=True)
#     sale_end_date = models.DateField(null=True, blank=True)

class Support(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    message = models.CharField(max_length=1000)
    is_answered = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} : {self.message} on {self.date}"

class SupportAnswer(models.Model):
    latest_message = models.ForeignKey(Support, on_delete=models.CASCADE)
    answered_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    response = models.CharField(max_length=1000)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.response

class SlideShowImage(models.Model):
    title = models.CharField(max_length=20)
    image = models.ImageField(upload_to=slide_show_upload_path, max_length=255)
    order = models.PositiveIntegerField()

    def __str__(self):
        return self.title

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.PositiveIntegerField()
    timestamp = models.DateTimeField()

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    in_cart = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.id}: {self.user.username} put {self.item.name} in cart'

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    is_wishlisted = models.BooleanField(default=False)

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item, through='TransactionItem')
    date = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    # is_purchased = models.BooleanField(default=False)

    def calculate_total(self):
        total = Decimal('0.00')
        for transaction_item in self.transactionitem_set.all():
            total += transaction_item.quantity * transaction_item.item.price
        self.total_price = total
        self.save()

    def __str__(self):
        return f'Transaction {self.id} by {self.user.username} on {self.date}'

class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.item.name} (x{self.quantity}) in Transaction {self.transaction.id}'



class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.PositiveIntegerField()
    usage_limit = models.PositiveIntegerField()
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()