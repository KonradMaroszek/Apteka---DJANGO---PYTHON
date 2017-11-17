from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Product
from django.core.exceptions import ObjectDoesNotExist
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy

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

def index_visitor(request):
    return render(request, 'pharmacy/index_visitor.html', {})

def add_to_basket(request):
    try:
        selected_product = get_object_or_404(Product,pk=request.POST['add_to_basket'])
    except (KeyError, ObjectDoesNotExist):
        return render(request, 'pharmacy/products.html', {'error_message' : "Cannot add this product to basket"})
    else:
        return render(request, 'pharmacy/basket.html', {'sucess_message': "Added new product to basket"})

class CreateProduct(CreateView):
    model = Product
    fields = ['name', 'price', 'amount', 'product_logo', 'description']

class UpdateProduct(UpdateView):
    model = Product
    fields = ['name', 'price', 'amount', 'product_logo', 'description']

class DeleteProduct(DeleteView):
    model = Product
    success_url = reverse_lazy('pharmacy:products')
