from django.contrib import admin

from store.models import Product, ReviewRating, Variation

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_avaible')
    prepopulated_fields = {'slug': ('product_name',)}

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value','is_active')

admin.site.register(Product, ProductAdmin)
admin.site.register(Variation)
admin.site.register(ReviewRating)
