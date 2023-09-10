from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

def item_image_upload_path(instance):
    return f'static/supplement_store/images/product_images/{instance.name}/'

class User(AbstractUser):
    address = models.CharField(default=None)
    birth = models.DateField(default='1900-01-01')

class Item(models.Model):
    CATEGORIES = (
        ('Protein powders','Protein powders'),
        ('Creatine','Creatine'),
        ('Pre-Workouts','Pre-Workouts'),
        ('Post-Workouts','Post-Workouts'),
        ('Test Boosters','Test Boosters'),
        ('Mass Gainers', 'Mass Gainers'),
        ('Weight Loss', 'Weight Loss'),
        ('Vitamins and Minerals','Vitamins and Minerals'),
        ('Meal Replacements','Meal Replacements'),
        ('Clothing','Clothing'),
        ('Workout Accessories','Workout Accessories'),
        
    )

    name = models.CharField(max_length=20)
    fullname = models.CharField(max_length=60)
    category = models.CharField(choices=CATEGORIES)
    subcategory = models.CharField(max_length=50)
    brand = models.CharField(max_length=30)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_on_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_start_date = models.DateTimeField(null=True, blank=True)
    sale_end_date = models.DateTimeField(null=True, blank=True)
    weight = models.PositiveIntegerField(null=True, blank=True)
    flavor = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=5, null=True, blank=True)
    size = models.CharField(max_length=3, null=True, blank=True)
    color = models.CharField(max_length=10, null=True, blank=True)
    is_new = models.BooleanField(default=False)
    popularity = models.IntegerField(default=0)
    main_image = models.ImageField(upload_to=item_image_upload_path)
    image1 = models.ImageField(upload_to=item_image_upload_path, blank=True, null=True)
    image2 = models.ImageField(upload_to=item_image_upload_path, blank=True, null=True)
    image3 = models.ImageField(upload_to=item_image_upload_path, blank=True, null=True)

class InStock(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    is_available = models.BooleanField()
    quantity = models.PositiveIntegerField()

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

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    is_wishlisted = models.BooleanField(default=False)

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    date = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_purchased = models.BooleanField(default=False)

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.PositiveIntegerField()
    usage_limit = models.PositiveIntegerField()
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()