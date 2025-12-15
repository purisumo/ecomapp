from django.contrib import admin
from django.apps import apps
# from .models import *

# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('username', 'user_type', 'email', 'created_at')
#     list_filter = ('user_type',)
#     search_fields = ('username', 'email')

# @admin.register(Shop)
# class ShopAdmin(admin.ModelAdmin):
#     list_display = ('name', 'seller', 'rating', 'is_active')
#     list_filter = ('is_active',)
#     search_fields = ('name', 'seller__username')

# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'parent')
#     search_fields = ('name',)

# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('name', 'shop', 'price', 'stock', 'is_available')
#     list_filter = ('is_available', 'shop')
#     search_fields = ('name', 'description')

# @admin.register(Inventory)
# class InventoryAdmin(admin.ModelAdmin):
#     list_display = ('product', 'stock', 'low_stock_threshold')
#     search_fields = ('product__name',)

# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('order_number', 'customer', 'shop', 'total_amount', 'status')
#     list_filter = ('status',)
#     search_fields = ('order_number', 'customer__username')

# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ('order', 'product', 'quantity', 'subtotal')
#     search_fields = ('order__order_number', 'product__name')

# @admin.register(Review)
# class ReviewAdmin(admin.ModelAdmin):
#     list_display = ('product', 'customer', 'rating', 'created_at')
#     list_filter = ('rating',)
#     search_fields = ('product__name', 'customer__username')

# @admin.register(Chat)
# class ChatAdmin(admin.ModelAdmin):
#     list_display = ('customer', 'shop', 'created_at')
#     search_fields = ('customer__username', 'shop__name')

# @admin.register(Message)
# class MessageAdmin(admin.ModelAdmin):
#     list_display = ('chat', 'sender', 'sent_at', 'is_read')
#     list_filter = ('is_read',)
#     search_fields = ('sender__username', 'content')

# @admin.register(Notification)
# class NotificationAdmin(admin.ModelAdmin):
#     list_display = ('user', 'type', 'is_read', 'created_at')
#     list_filter = ('type', 'is_read')
#     search_fields = ('user__username', 'content')

# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display = ('customer', 'created_at')
#     search_fields = ('customer__username',)

# @admin.register(CartItem)
# class CartItemAdmin(admin.ModelAdmin):
#     list_display = ('cart', 'product', 'quantity')
#     search_fields = ('cart__customer__username', 'product__name')

# @admin.register(Wishlist)
# class WishlistAdmin(admin.ModelAdmin):
#     list_display = ('customer', 'created_at')
#     search_fields = ('customer__username',)

# @admin.register(Payment)
# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ('order', 'amount', 'status', 'payment_method')
#     list_filter = ('status',)
#     search_fields = ('order__order_number', 'transaction_id')



# Register your models here.
app_config = apps.get_app_config('shop')

# Iterate through models in the app
for model in app_config.get_models():
    # Exclude non-editable fields
    non_editable_fields = ['id', 'created_at', 'updated_at', 'last_updated', 'sent_at', 'order_number', 'followed_at']  # Add other non-editable fields if needed

    # Create a custom admin class dynamically
    admin_class = type(
        f'{model.__name__}Admin',
        (admin.ModelAdmin,),
        {
            'list_display': [field.name for field in model._meta.fields],
            'list_editable': [
                field.name
                for field in model._meta.fields
                if field.name not in non_editable_fields
            ],
            'list_display_links': ['id'],  # Make the 'id' field clickable
        }
    )

    # Register the model with the custom admin class
    admin.site.register(model, admin_class)