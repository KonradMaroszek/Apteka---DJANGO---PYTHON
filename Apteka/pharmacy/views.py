from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Product
from django.core.exceptions import ObjectDoesNotExist

from django.views import generic

class ProductDetailView(generic.DetailView):
    model = Product
    template_name = 'pharmacy/product_detail.html'

class AllProducts(generic.ListView):
    template_name = 'pharmacy/products.html'
    context_object_name = 'all_products'

    def get_queryset(self):
        return Product.objects.all()

def index(request):
    return render(request, 'pharmacy/index.html', {})

def add_to_basket(request):
    try:
        selected_product = get_object_or_404(Product,pk=request.POST['add_to_basket'])
    except (KeyError, ObjectDoesNotExist):
        return render(request, 'pharmacy/products.html', {'error_message' : "Cannot add this product to basket"})
    else:
        return render(request, 'pharmacy/basket.html', {'sucess_message': "Added new product to basket"})