from django.db import models
from django.urls import reverse
from accounts.models import Account

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='store/category_images', blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self) -> str:
        return self.category_name

class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField(upload_to='store/product_images')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.product_name
    
    def get_url(self):
        return reverse('product_detail', args=[self.category.slug,self.slug])
    

    

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.cart_id
    
class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, related_name='cart_item')
    variation = models.ManyToManyField('Variation', blank=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.product.product_name 
    def sub_total(self):
        return self.product.price * self.quantity
    


class VariationManger(models.Manager):
    def colors(self):
        return super(VariationManger, self).filter(variation_category='color', is_active=True)

    def sizes(self):
        return super(VariationManger, self).filter(variation_category='size', is_active=True)
    



class Variation(models.Model):
    VARIATION_CATEGORY_CHOICES = (
        ('color','color'),
        ('size','size')
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=VARIATION_CATEGORY_CHOICES)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManger()

    def __str__(self) -> str:
        return self.variation_category + " " + self.variation_value


    







