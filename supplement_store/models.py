from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from decimal import Decimal

from .countries import COUNTRIES

def item_image_upload_path(instance, filename):
    return f'supplement_store/static/supplement_store/images/product_images/{instance.fullname}/{instance.id}_{filename}'

def slide_show_upload_path(instance, filename):
    return f'supplement_store/static/supplement_store/images/slide_show_images/{timezone.now().strftime("%Y-%m-%d_%H-%M-%S")}_{filename}'

class User(AbstractUser):
    is_support = models.BooleanField(default=False)
    address = models.CharField(null=True, blank=True)
    city = models.CharField(null=True, blank=True)
    state = models.CharField(null=True, blank=True)
    country = models.TextField(choices=COUNTRIES.items(), null=True, blank=True)
    zipcode = models.CharField(null=True, blank=True)
    phone = models.CharField(null=True, blank=True)
    birth = models.DateField(null=True, blank=True)

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
    flavor = models.CharField(max_length=35, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    size = models.CharField(max_length=3, null=True, blank=True)
    color = models.CharField(max_length=10, null=True, blank=True)
    is_new = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=timezone.now)
    popularity = models.IntegerField(default=0)
    main_image = models.ImageField(upload_to=item_image_upload_path, max_length=255)
    image1 = models.ImageField(upload_to=item_image_upload_path, blank=True, null=True, max_length=255)
    image2 = models.ImageField(upload_to=item_image_upload_path, blank=True, null=True, max_length=255)
    image3 = models.ImageField(upload_to=item_image_upload_path, blank=True, null=True, max_length=255)

    def __str__(self):
        return f'{self.id}: {self.fullname}, Available: {self.is_available}, Flavor: {self.flavor}, Popularity: {self.popularity}, Quantity: {self.quantity}'

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

    def __str__(self):
        return f'{self.id}: Wishlisted item {self.item.fullname} by user {self.user.username}'

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('canceled', 'Canceled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item, through='TransactionItem')
    date = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(choices=STATUS_CHOICES, default='pending')
    
    email = models.EmailField(null=False, blank=False)
    first_name = models.CharField(null=False, blank=False)
    last_name = models.CharField(null=False, blank=False)
    phone = models.CharField(null=False, blank=False)
    address = models.CharField(null=False, blank=False)
    city = models.CharField(null=False, blank=False)
    zipcode = models.CharField(null=False, blank=False)
    state = models.CharField(null=True, blank=True)
    country = models.TextField(choices=COUNTRIES.items(), null=False, blank=False)

    def calculate_total(self):
        total = Decimal('0.00')
        for transaction_item in self.transactionitem_set.all():
            total += transaction_item.quantity * transaction_item.item.price
        self.total_price = total
        self.save()

    def __str__(self):
        return f'Transaction {self.id} by {self.user.username} on {self.date}, email sent: on {self.email}'

class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.item.name} (x{self.quantity}) in Transaction {self.transaction.id}'
    
class Newsletter(models.Model):
    email = models.EmailField(blank=False, null=False)

    def __str__(self):
        return f'ID: {self.id}, email: {self.email} registered for newsletter'