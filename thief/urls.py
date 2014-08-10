from django.conf.urls import patterns, include, url

# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'thief.products.views.products', name='home'),
    
    url(r'^auction/global_configs$', 'thief.auction.views.global_configs', name='auction_configs'),
    url(r'^auction/global_configs/edit$', 'thief.auction.views.edit_global_configs', name='edit_auction_configs'),
    url(r'^auction/keywords$', 'thief.auction.views.keywords', name='auction_keywords'),

    url(r'^auction/(?P<type>((yahoo)|(ruten)))$', 'thief.auction.views.auction_types', name='auction_types'),
    url(r'^auction/(?P<type>((yahoo)|(ruten)))/create$', 'thief.auction.views.create_auction_type', name='create_auction_type'),
    url(r'^auction/(?P<type>((yahoo)|(ruten)))/edit/(?P<id>\d+)$', 'thief.auction.views.edit_auction_type', name='edit_auction_type'),
    url(r'^auction/(?P<type>((yahoo)|(ruten)))/delete$', 'thief.auction.views.delete_auction_type', name='delete_auction_type'),
    
    url(r'^vendor/search$', 'thief.vendors.views.search_product', name='search'),
    url(r'^vendor/query.(?P<format>(json))$', 'thief.vendors.views.query', name='query_vendor'),

    url(r'^products$', 'thief.products.views.products', name='products'),
    
    url(r'^products/download/(?P<auction_type>((yahoo)|(ruten))).zip$', 'thief.products.views.download_csv', name='download_products_csv'),
    url(r'^products/upload$', 'thief.products.views.upload_csv', name='upload_products_csv'),

    url(r'^product/(?P<id>\d+)$', 'thief.products.views.product', name='product'),
    url(r'^product/(?P<id>\d+)/prepare$', 'thief.products.views.prepare_product', name='prepare_product'),
    url(r'^product/(?P<id>\d+)/edit$', 'thief.products.views.edit_product', name='edit_product'),
    url(r'^product/(?P<id>\d+)/edit_image$', 'thief.products.views.edit_image', name='edit_product_images'),
    
    url(r'^product_image/(?P<id>\d+)$', 'thief.products.views.product_image', name='product_image'),
)
