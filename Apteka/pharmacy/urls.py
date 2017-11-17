from django.conf.urls import url
from . import views

app_name = 'pharmacy'

urlpatterns = [
    #/pharmacy/
    url(r'^$', views.index, name='index'),
    #/pharmacy/products
    url(r'^products/$', views.AllProducts.as_view(), name='products'),
    #pharmacy/products/1
    url(r'^products/(?P<pk>[0-9]+)/$', views.ProductDetailView.as_view(), name='product_detail'),
    #pharmacy/add_to_basket
    url(r'^add_to_basket/$', views.add_to_basket, name='add_to_basket'),
    # pharmacy/product/add
    url(r'^product/add/$', views.CreateProduct.as_view(), name='add_product'),
    # pharmacy/product/edit/2/
    url(r'^product/edit/(?P<pk>[0-9]+)/$', views.UpdateProduct.as_view(), name='update_product'),
    # pharmacy/delete/2
    url(r'^product/delete/(?P<pk>[0-9]+)/$', views.DeleteProduct.as_view(), name='delete_product'),

]