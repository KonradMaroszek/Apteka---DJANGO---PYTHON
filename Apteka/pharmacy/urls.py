from django.conf.urls import url
from . import views

app_name = 'pharmacy'

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^logout/$', views.logout_view, name='logout'),

    url(r'^register/$', views.UserFormView.as_view(), name='register'),

    url(r'^signin/$', views.SignInView.as_view(), name='sign_in'),

    url(r'^products/$', views.AllProducts.as_view(), name='products'),

    url(r'^products/(?P<pk>[0-9]+)/$', views.ProductDetailView.as_view(), name='product_detail'),

    url(r'^basket/$', views.basket_view, name='basket'),

    url(r'^add_to_basket/$', views.add_to_basket, name='add_to_basket'),

    url(r'^product/add/$', views.CreateProduct.as_view(), name='add_product'),

    url(r'^product/edit/(?P<pk>[0-9]+)/$', views.UpdateProduct.as_view(), name='update_product'),

    url(r'^product/delete/(?P<pk>[0-9]+)/$', views.DeleteProduct.as_view(), name='delete_product'),

    url(r'^pay/$', views.pay_view, name='pay'),

    url(r'^add_pay/$', views.add_pay_view, name='add_pay'),

    url(r'^history/$', views.history_view, name='history'),
]