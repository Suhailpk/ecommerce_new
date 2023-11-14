from django.contrib import admin
from .models import *

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name','slug']
    prepopulated_fields = {
        'slug':('category_name',)
    }

admin.site.register(Category, CategoryAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name','slug','price','category','stock']
    prepopulated_fields = {
        'slug':('product_name',)
    }

admin.site.register(Product, ProductAdmin)

admin.site.register(Cart)
admin.site.register(CartItem)

class VariationAdmin(admin.ModelAdmin):
    list_display = ['product', 'variation_category', 'variation_value', 'is_active']
    list_editable = ['is_active']
    list_filter = ['product', 'variation_category', 'variation_value']

admin.site.register(Variation, VariationAdmin)
