from django.conf.urls import url
from . import views

urlpatterns = [
    #/apteka/
    url(r'^$', views.index, name='index'),
    #/apteka/products
    url(r'^products/$', views.products, name='products'),
    #apteka/products/1
    url(r'^products/(?P<product_id>[0-9]+)/$', views.product_detail, name='product_detail'),
]