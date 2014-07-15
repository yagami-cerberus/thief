from django.conf.urls import patterns, include, url

# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'thief.products.views.products', name='home'),
    
    url(r'^auction/(?P<type>((yahoo)|(ruten)))$', 'thief.auction.views.auction_types', name='auction_types'),
    url(r'^auction/(?P<type>((yahoo)|(ruten)))/create$', 'thief.auction.views.create_auction_type', name='create_auction_type'),
    url(r'^auction/(?P<type>((yahoo)|(ruten)))/edit/(?P<id>\d+)$', 'thief.auction.views.edit_auction_type', name='edit_auction_type'),
    url(r'^auction/(?P<type>((yahoo)|(ruten)))/delete$', 'thief.auction.views.delete_auction_type', name='delete_auction_type'),
    
    
    url(r'^vendor/search$', 'thief.products.views.search_product', name='search'),
    url(r'^vendor/query.(?P<format>(json))$', 'thief.products.views.query_vendor', name='query_vendor'),

    url(r'^product$', 'thief.products.views.products', name='products'),
    url(r'^product/create$', 'thief.products.views.create_product', name='create_product'),
    url(r'^product/(?P<id>\d+)$', 'thief.products.views.product', name='product'),
    url(r'^product/(?P<id>\d+)/edit_meta$', 'thief.products.views.edit_meta', name='edit_product_meta'),
    url(r'^product/(?P<id>\d+)/edit_image$', 'thief.products.views.edit_image', name='edit_product_images'),
    
    url(r'^product_image/(?P<id>\d+)$', 'thief.products.views.product_image', name='product_image'),
    # url(r'^product/image/(?P<id>\d+)$', 'thief.products.views.product_image', name='product_image'),
)
