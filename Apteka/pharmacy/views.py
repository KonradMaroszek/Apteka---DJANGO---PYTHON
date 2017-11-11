from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Product
from django.core.exceptions import ObjectDoesNotExist

def index(request):
    return HttpResponse("<h1>This is APteka</h1>")

def products(request):
    all_products = Product.objects.all()
    return render(request, 'pharmacy/products.html', {'all_products' : all_products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'pharmacy/product_detail.html', {'product': product})

def add_to_basket(request):
    try:
        selected_product = get_object_or_404(Product,pk=request.POST['add_to_basket'])
    except (KeyError, ObjectDoesNotExist):
        return render(request, 'pharmacy/products.html', {'error_message' : "Cannot add this product to basket"})
    else:
        return render(request, 'pharmacy/index.html', {'message': "Added new product"})