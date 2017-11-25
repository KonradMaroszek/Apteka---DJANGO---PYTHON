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

from .forms import UserForm
from .models import Product


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


@login_required()
@permission_required('pharmacy.add_basket', 'pharmacy.delete_basket', 'pharmacy.change_basket')
def basket_view(request):
    return render(request, 'pharmacy/basket.html', get_permissions_to_be_passed_to_template(request))


class AllProducts(LoginRequiredMixin, generic.ListView):
    template_name = 'pharmacy/products.html'
    context_object_name = 'all_products'

    def get_queryset(self):
        return Product.objects.all()

    def get_context_data(self, **kwargs):
        context = super(AllProducts, self).get_context_data(**kwargs)
        context.update(get_permissions_to_be_passed_to_template(self.request))
        return context


def index(request):
    if request.user.is_authenticated:
        return render(request, 'pharmacy/index.html', get_permissions_to_be_passed_to_template(request))
    else:
        return render(request, 'pharmacy/index_visitor.html', {})


@login_required()
def add_to_basket(request):
    try:
        selected_product = get_object_or_404(Product, pk=request.POST['add_to_basket'])
    except (KeyError, ObjectDoesNotExist):
        return render(request, 'pharmacy/products.html', {'error_message': "Cannot add this product to basket"})
    else:
        return render(request, 'pharmacy/basket.html', {'sucess_message': "Added new product to basket"})


class CreateProduct(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = 'pharmacy.add_product'
    raise_exception = True
    model = Product
    fields = ['name', 'price', 'amount', 'product_logo', 'description']


@login_required()
def logout_view(request):
    logout(request)
    return redirect("pharmacy:index")


class UpdateProduct(PermissionRequiredMixin, UpdateView):
    permission_required = 'pharmacy.change_product'
    raise_exception = True
    model = Product
    fields = ['name', 'price', 'amount', 'product_logo', 'description']


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
            user.groups.set('pharmacy.client')
            user.save()

            user = authenticate(username=username, password=password)

            if user is not None:

                if user.is_active:
                    login(request, user)
                    return redirect('..')

        return render(request, self.template_name, {'form': form})
