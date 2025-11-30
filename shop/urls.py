from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),

    path('seller/list_of_users/', views.admin_list_of_users, name='list_of_users'),

    path('seller/dashboard/', views.seller_dashboard_view, name='seller_dashboard'),
    path('seller/messages/', views.seller_messages_view, name='seller_messages'),
    path('seller/messages/<int:chat_id>/', views.seller_messages_view, name='seller_messages'),
    path('seller/shop/edit/', views.edit_shop_view, name='edit_shop'),
    
    path('seller/products/', views.seller_products_view, name='seller_products'),
    path('seller/product/add/', views.add_product_view, name='add_product'),
    path('seller/product/product_info/<int:product_id>/', views.product_info_view, name='product_info'),
    path('seller/product/edit/<int:product_id>/', views.edit_product_view, name='edit_product'),
    path('seller/product/delete/<int:product_id>/', views.delete_product_view, name='delete_product'),
    path('seller/order/update/<int:order_id>/', views.update_order_view, name='update_order'),
    path('seller/categories/', views.seller_categories_view, name='seller_categories'),
    path('seller/categories/create/', views.create_category_view, name='create_category'),
    path('seller/categories/edit/<int:category_id>/', views.edit_category_view, name='edit_category'),
    path('seller/categories/delete/<int:category_id>/', views.delete_category_view, name='delete_category'),
    path('admin/orders/', views.admin_orders_view, name='admin_orders'),
    path('admin/notifications/', views.admin_notifications_view, name='admin_notifications'),


    path('shop_info/<int:shop_id>/', views.shop_info_view, name='shop_info'),
    path('shop_info/<int:shop_id>/toggle_follow/', views.toggle_follow, name='toggle_follow'),
    path('chat/', views.chat_view, name='chat'),
    path('chat/<int:shop_id>/', views.chat_view, name='chat'),
    path('messages/<int:chat_id>/', views.get_messages, name='get_messages'),
    path('send_message/<int:chat_id>/', views.send_message, name='send_message'),


    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),


    path('cart/', views.cart_view, name='cart'),
    path('api/cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('api/cart/update/<int:cart_item_id>/', views.update_cart_item, name='update_cart_item'),
    path('api/cart/delete/<int:cart_item_id>/', views.delete_cart_item, name='delete_cart_item'),

    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('api/wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('api/wishlist/delete/<int:product_id>/', views.delete_from_wishlist, name='delete_from_wishlist'),
    path('orders/', views.orders_view, name='orders'),
    path('api/orders/create/', views.create_order, name='create_order'),
    path('api/orders/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('reviews/', views.reviews_view, name='reviews'),
    path('api/reviews/add/<int:product_id>/', views.add_review, name='add_review'),
    path('api/reviews/update/<int:review_id>/', views.update_review, name='update_review'),
    path('api/reviews/delete/<int:review_id>/', views.delete_review, name='delete_review'),

    path('products/', views.products_view, name='products'),
    path('search-products/', views.search_products_ajax, name='search-products'),
    path('product/<int:product_id>/', views.product_detail_view, name='product_detail'),
    path('api/product/<int:product_id>/order/', views.order_product_view, name='order_product'),
    path('api/buy-now/<int:product_id>/', views.buy_now, name='buy_now'),

    path('profile/', views.profile, name="profile"),
    path('checkout/', views.checkout, name="checkout"),
    path('checkout_success/', views.checkout_success, name="checkout_success"),
    path('payment/gcash/callback/', views.gcash_callback, name='gcash_callback'),
    path('payment/gcash/failed/', views.gcash_failed, name='gcash_failed'),
    path('notification/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('payment/gcash/process', views.process_gcash_payment, name="process_gcash_payment"),
    path('payment/gcash/<str:session_id>/', views.gcash_payment, name="gcash_payment"),
]