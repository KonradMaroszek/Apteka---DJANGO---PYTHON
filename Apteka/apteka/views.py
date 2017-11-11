from django.http import HttpResponse
from django.shortcuts import render
from .models import Product

def index(request):
    return HttpResponse("<h1>This is APteka</h1>")

def products(request):
    all_products = Product.objects.all()
    context = {'all_products' : all_products}
    return render(request, 'apteka/products.html', context)

def product_detail(request, product_id):
    return HttpResponse("<h2>Details for product id:"  + str(product_id) +  "</h2>")