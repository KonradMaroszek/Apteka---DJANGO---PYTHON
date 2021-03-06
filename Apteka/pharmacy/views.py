from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.views import generic
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import Group

from .forms import UserForm
from .models import Product
from .models import History
import ast
import hashlib
import time

def get_permissions_to_be_passed_to_template(request):
    return {'has_{}_permission'.format(perm.split('.')[1]): request.user.has_perm(perm)
            for perm in get_all_existing_model_permissions()}


def get_all_existing_model_permissions():
    models = ['product', 'basket']
    for perm in ['add', 'change', 'delete']:
        for model in models:
            yield 'pharmacy.{}_{}'.format(perm, model)


class ProductDetailView(LoginRequiredMixin, generic.DetailView):
    model = Product
    template_name = 'pharmacy/product_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context.update(get_permissions_to_be_passed_to_template(self.request))
        product = context['product']
        product.discount_price = float((100 - int(product.discount)) / 100.0 * float(product.price))
        return context


class AllProducts(LoginRequiredMixin, generic.ListView):
    template_name = 'pharmacy/products.html'
    context_object_name = 'all_products'

    def get_queryset(self):
        products = Product.objects.all()
        for product in products:
            product.discount_price = float((100 - int(product.discount)) / 100.0 * float(product.price))
        return products

    def get_context_data(self, **kwargs):
        context = super(AllProducts, self).get_context_data(**kwargs)
        context.update(get_permissions_to_be_passed_to_template(self.request))
        return context


def index(request):
    if request.user.is_authenticated:
        return render(request, 'pharmacy/index.html', get_permissions_to_be_passed_to_template(request))
    else:
        return render(request, 'pharmacy/index_visitor.html', {})


def get_basket_products(request, selected_product):
    basket_products = {}  # id : basket_product
    basket_product = {}  # id, name, price, amount, url, coupon
    if 'basket_products' in request.COOKIES:
        basket_products = ast.literal_eval(request.COOKIES['basket_products'])

    if selected_product is not None and selected_product.id in basket_products:
        basket_product = basket_products[selected_product.id]
        action = request.POST.get('basket_product_op', '')
        if action == 'minus':
            if basket_product['amount'] == 1:
                del basket_products[selected_product.id]
            elif basket_product['amount'] > 0:
                basket_product['amount'] = basket_product['amount'] - 1
        else:
            basket_product['amount'] = basket_product['amount'] + 1
    elif selected_product is not None:
        basket_product = {'id': selected_product.id, 'name': selected_product.name, 'price': selected_product.price, 'discount': selected_product.discount,
                          'discount_price': float((100 - int(selected_product.discount)) / 100.0 * float(selected_product.price)), 'amount': 1, 'url': selected_product.product_logo.url, 'coupon' : 1.0}
        basket_products[selected_product.id] = basket_product

    return basket_products

def get_basket_price(basket_products):
    price = 0.0
    for basket_product in basket_products.values():
        price = price + (float(basket_product['amount']) * float(basket_product['discount_price']) * float(basket_product['coupon']))

    if price >= 200:
        price = price * 0.85
    elif price >= 100:
        price = price * 0.9
    elif price >= 50:
        price = price * 0.95

    return price

@login_required()
@permission_required('pharmacy.add_basket', 'pharmacy.delete_basket', 'pharmacy.change_basket')
def basket_view(request):
    basket_products = get_basket_products(request, None)
    price = get_basket_price(basket_products)

    context = {'basket_products' : basket_products, 'basket_price' : price}
    permissions = get_permissions_to_be_passed_to_template(request)
    context.update(permissions)

    return render(request, 'pharmacy/basket.html', context)

@login_required()
def add_to_basket(request):
    coupon = request.POST.get('basket_coupon', '')
    if (coupon is not ''):
        basket_products = get_basket_products(request, None)
        discount = 1.0
        if (coupon == 'I WANT 20 DISCOUNT'):
           discount = 0.8
        elif (coupon == 'I WANT 40 DISCOUNT'):
            discount = 0.6
        elif (coupon == 'I WANT 60 DISCOUNT'):
            discount = 0.4
        for basket_product in basket_products.values():
            basket_product['coupon'] = discount
        price = get_basket_price(basket_products)

        context = {'sucess_message': "Updated basket", 'basket_products': basket_products, 'basket_price': price}
        permissions = get_permissions_to_be_passed_to_template(request)
        context.update(permissions)

        response = render(request, 'pharmacy/basket.html', context)
        response.set_cookie('basket_products', basket_products)
        return response
    else:
        try:
            selected_product = get_object_or_404(Product, pk=request.POST['add_to_basket'])
        except (KeyError, ObjectDoesNotExist):

            context = {'error_message': "Cannot add this product to basket"}
            permissions = get_permissions_to_be_passed_to_template(request)
            context.update(permissions)

            return render(request, 'pharmacy/products.html', context)
        else:
            basket_products = get_basket_products(request, selected_product)
            price = get_basket_price(basket_products)

            context = {'sucess_message': "Updated basket", 'basket_products' : basket_products, 'basket_price' : price}
            permissions = get_permissions_to_be_passed_to_template(request)
            context.update(permissions)

            response = render(request, 'pharmacy/basket.html', context)
            response.set_cookie('basket_products', basket_products)
            return response

@login_required()
def pay_view(request):
    basket_products = get_basket_products(request, None)
    price = get_basket_price(basket_products)
    number = int((hashlib.md5(str(time.time()).encode())).hexdigest(), 16)
    number = number % 100000000

    context = {'price' : price, 'number' : number}
    permissions = get_permissions_to_be_passed_to_template(request)
    context.update(permissions)

    return render(request, 'pharmacy/pay.html', context)

@login_required()
def add_pay_view(request):
    history_order = request.POST.get('number', 0)
    history_basket = get_basket_products(request, None)
    history_price = get_basket_price(history_basket)
    History.objects.create(user=request.user, order=history_order, price=history_price, status='Order in execution', basket=history_basket)
    response = render(request, 'pharmacy/index.html', get_permissions_to_be_passed_to_template(request))
    response.delete_cookie('basket_products')
    return response

@login_required()
def sale_view(request):
    products = Product.objects.all()
    for product in products:
        product.discount_price = float((100 - int(product.discount)) / 100.0 * float(product.price))

    context = {'all_products': products}
    permissions = get_permissions_to_be_passed_to_template(request)
    context.update(permissions)

    return render(request, 'pharmacy/sale.html', context)

@login_required()
def history_view(request):
    history = History.objects.filter(user=request.user, status='Done')
    for entry in history:
        entry.basket = ast.literal_eval(entry.basket)

    context = {'history' : history}
    permissions = get_permissions_to_be_passed_to_template(request)
    context.update(permissions)

    return render(request, 'pharmacy/history.html', context)


@login_required()
def history_execution_view(request):
    history = History.objects.filter(user=request.user, status='Order in execution')
    for entry in history:
        entry.basket = ast.literal_eval(entry.basket)

    context = {'history' : history}
    permissions = get_permissions_to_be_passed_to_template(request)
    context.update(permissions)

    return render(request, 'pharmacy/history.html', context)


@login_required()
def history_status_view(request):
    history = History.objects.filter(status='Order in execution')
    for entry in history:
        entry.basket = ast.literal_eval(entry.basket)

    context = {'history' : history}
    permissions = get_permissions_to_be_passed_to_template(request)
    context.update(permissions)

    return render(request, 'pharmacy/history_status.html', context)


@login_required()
def history_status_change_view(request):
    History.objects.filter(order=request.POST.get('order', 0)).update(status='Done')
    history = History.objects.filter(status='Order in execution')
    for entry in history:
        entry.basket = ast.literal_eval(entry.basket)

    context = {'history' : history, 'message' : 'Status updated'}
    permissions = get_permissions_to_be_passed_to_template(request)
    context.update(permissions)

    return render(request, 'pharmacy/history_status.html', context)

class CreateProduct(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = 'pharmacy.add_product'
    raise_exception = True
    model = Product
    fields = ['name', 'price', 'amount', 'product_logo', 'description', 'discount']


@login_required()
def logout_view(request):
    logout(request)
    return redirect("pharmacy:index")


class UpdateProduct(PermissionRequiredMixin, UpdateView):
    permission_required = 'pharmacy.change_product'
    raise_exception = True
    model = Product
    fields = ['name', 'price', 'amount', 'product_logo', 'description', 'discount']


class DeleteProduct(PermissionRequiredMixin, DeleteView):
    permission_required = 'pharmacy.delete_product'
    raise_exception = True
    model = Product
    success_url = reverse_lazy('pharmacy:products')


class SignInView(LoginView):
    template_name = 'pharmacy/login_form.html'
    redirect_authenticated_user = True


class UserFormView(View):
    form_class = UserForm
    template_name = 'pharmacy/registration_form.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            client_group = Group.objects.get(name='pharmacy.client')
            client_group.user_set.add(user)

            user = authenticate(username=username, password=password)

            if user is not None:

                if user.is_active:
                    login(request, user)
                    return redirect('..')

        return render(request, self.template_name, {'form': form})
