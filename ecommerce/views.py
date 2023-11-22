from django.shortcuts import render

from store.models import Product, ReviewRating

def home(request):
    products = Product.objects.all().filter(is_avaible=True).order_by('created_date')

    reviews = None
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True) # type: ignore

    context = {
        'products': products,
        'reviews': reviews,
    }


    return render(request, 'home.html', context)
