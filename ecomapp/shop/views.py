import string
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.http import require_POST

from shop.paymongo import PayMongoAPI
from .models import *
from .forms import *
from .utils import *
from django.db.models import Sum, Count
from django.utils import timezone
import json
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from datetime import datetime, time, timedelta, date
from django.db.models import Avg
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Prefetch
from collections import defaultdict
from decimal import Decimal
from django.db import transaction

def home(request):
    trigger_login_modal = request.GET.get('login_required') == 'true'
    next_url = request.GET.get('next') or request.POST.get('next')

    if trigger_login_modal: 
        if next_url and request.user.is_authenticated: return redirect(next_url)
        messages.error(request, 'You must login first!')

    products = Product.objects.filter(is_available=True)
    
    return render(request, 'shop/home.html', {'products': products, 'trigger_login_modal': trigger_login_modal})

@login_required
def shop_list_view(request):
    # Get shops where the user can chat (either as a customer or seller)
    if request.user.user_type == 'customer':
        # Customers can chat with any shop
        shops = Shop.objects.all()
    else:
        # Sellers can only chat with customers for their own shops
        shops = Shop.objects.filter(seller=request.user)
    
    # Optionally, include existing chats for context
    chats = Chat.objects.filter(customer=request.user) if request.user.user_type == 'customer' else Chat.objects.filter(shop__seller=request.user)
    chat_dict = {chat.shop.id: chat for chat in chats}

    # Prepare data for template
    shop_data = []
    for shop in shops:
        shop_info = {
            'id': shop.id,
            'name': shop.name,  # Adjust based on your Shop model fields
            'has_chat': shop.id in chat_dict,
            'chat_id': chat_dict.get(shop.id).id if shop.id in chat_dict else None
        }
        shop_data.append(shop_info)

    return render(request, 'shop/chatlist.html', {'shops': shop_data, 'user': request.user})

@login_required
def seller_messages_view(request, chat_id=None):
    if request.user.user_type != 'seller':
        return render(request, 'seller/seller_messages.html', {'error': 'Only sellers can view messages'})
    
    shop = get_object_or_404(Shop, seller=request.user)
    chats = Chat.objects.filter(shop=shop, messages__isnull=False).distinct().order_by('-created_at')
    selected_chat = None
    error = None

    # Populate chats with metadata
    for chat in chats:
        chat.latest_message = chat.messages.last().content if chat.messages.exists() else None
        chat.latest_message_date = chat.messages.last().sent_at if chat.messages.exists() else None
        chat.latest_message_time = chat.messages.last().sent_at if chat.messages.exists() else None

    if chat_id:
        selected_chat = get_object_or_404(Chat, id=chat_id, shop=shop)

        if request.user != selected_chat.shop.seller:
            messages.error(request, 'Unauthorized access')
            return redirect('shop:seller_messages')
            
        selected_chat.is_read = True
        selected_chat.save()

    context = {
        'shop': shop,
        'chats': chats,
        'selected_chat': selected_chat,
        'selected_chat_id': selected_chat.id if selected_chat else 0,
        'user': request.user,
        'error': error,
        'messages_url': reverse('shop:get_messages', args=[0]),
        'send_url': reverse('shop:send_message', args=[0]),
    }

    return render(request, 'seller/seller_messages.html', context)


@login_required
def shop_info_view(request, shop_id):
    if not request.user.is_active:
        return redirect('shop:home')

    selected_shop = get_object_or_404(Shop, id=shop_id)
    products = Product.objects.filter(shop=selected_shop).order_by('-is_available', '-created_at')

    # Get product IDs in user's cart
    try:
        cart = Cart.objects.get(customer=request.user)
        cart_product_ids = set(cart.items.values_list('product_id', flat=True))
    except Cart.DoesNotExist:
        cart_product_ids = set()

    # Mark products that are already in the cart
    for product in products:
        product.is_in_cart = product.id in cart_product_ids

    is_following = ShopFollower.objects.filter(user=request.user, shop=selected_shop).exists()
    followers_count = selected_shop.followers.count()

    listed_items_count = products.count()
    available_items_count = products.filter(is_available__gt=0).count()

    # Check if user can rate
    has_completed_order = OrderItem.objects.filter(
        order__customer=request.user,
        order__status='completed',
        product__shop=selected_shop
    ).exists()

    has_already_rated = ShopReview.objects.filter(customer=request.user, shop=selected_shop).exists()
    can_rate_this_shop = has_completed_order and not has_already_rated

    if request.method == 'POST':
        if 'rate-shop' in request.POST:
            if can_rate_this_shop:
                rating = int(request.POST.get('rating'))
                description = request.POST.get('description', '')

                # Save the review
                ShopReview.objects.create(
                    customer=request.user,
                    shop=selected_shop,
                    rating=rating,
                    description=description
                )

                # ✅ Update average rating
                average_rating = ShopReview.objects.filter(shop=selected_shop).aggregate(avg=Avg('rating'))['avg']
                selected_shop.rating = round(average_rating or 0, 1)
                selected_shop.save()

                # ✅ Notify the seller
                Notification.objects.create(
                    user=selected_shop.seller,
                    title="New shop rating",
                    content=f"{request.user.get_full_name()} has rated your shop '{selected_shop.name}' with {rating} stars.",
                    type="review"
                )

                messages.success(request, "Thank you for rating this shop!")
                return redirect('shop:shop_info', shop_id=shop_id)
            
            else:
                messages.error(request, "You are not allowed to rate this shop.")

    # Return shop reviews for display
    shop_reviews = ShopReview.objects.filter(shop=selected_shop).order_by('-created_at')

    return render(request, 'shop/shop_info.html', {
        'selected_shop': selected_shop,
        'products': products,
        'is_following': is_following,
        'followers_count': followers_count,
        'can_rate_this_shop': can_rate_this_shop,
        'shop_reviews': shop_reviews,
        'listed_items_count': listed_items_count,
        'available_items_count': available_items_count,
    })

@login_required
def toggle_follow(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    follow, created = ShopFollower.objects.get_or_create(user=request.user, shop=shop)

    if not created:
        follow.delete()
        return JsonResponse({'status': 'unfollowed', 'followers': shop.followers.count()})
    else:
        return JsonResponse({'status': 'followed', 'followers': shop.followers.count()})

@login_required
def chat_view(request, shop_id=None):
    shops = Shop.objects.all()
    selected_shop = None
    selected_chat = None
    error = None

    # Populate shops with chat and latest message data
    for shop in shops:
        chat = Chat.objects.filter(shop=shop, customer=request.user).first() if request.user.user_type == 'customer' else Chat.objects.filter(shop=shop, seller=request.user).first()
        shop.has_chat = chat is not None
        shop.chat_id = chat.id if chat else 0
        shop.latest_message = chat.messages.last().content if chat and chat.messages.exists() else None
        shop.latest_message_date = chat.messages.last().sent_at if chat and chat.messages.exists() else None
        shop.latest_message_time = chat.messages.last().sent_at if chat and chat.messages.exists() else None
        shop.is_message_read = chat.messages.last().is_read if chat and chat.messages.exists() else None

    if shop_id:
        selected_shop = get_object_or_404(Shop, id=shop_id)
        if request.user.user_type == 'customer':
            selected_chat, created = Chat.objects.get_or_create(customer=request.user, shop=selected_shop)
        elif request.user == selected_shop.seller:
            selected_chat = Chat.objects.filter(shop=selected_shop).first()
            if not selected_chat:
                error = 'No chat available'
        else:
            error = 'Unauthorized access'

        # Handle AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if error:
                return JsonResponse({'error': error}, status=403 if error == 'Unauthorized access' else 404)
            return JsonResponse({'chat_id': selected_chat.id})

    context = {
        'shops': shops,
        'selected_shop': selected_shop,
        'selected_chat_id': selected_chat.id if selected_chat else 0,  # Fixed default to 0
        'user': request.user,
        'error': error,
        'messages_url': reverse('shop:get_messages', args=[0]),
        'send_url': reverse('shop:send_message', args=[0]),
    }

    return render(request, 'shop/chatlist.html', context)

@login_required
def get_messages(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user != chat.customer and request.user != chat.shop.seller:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    messages = chat.messages.all().order_by('sent_at')
    messages_data = [{
        'sender': msg.sender.username,
        'content': msg.content,
        'sent_at': msg.sent_at.isoformat(),
        'is_read': msg.is_read
    } for msg in messages]
    
    chat.messages.filter(~Q(sender=request.user), is_read=False).update(is_read=True)
    
    return JsonResponse({'messages': messages_data})

@login_required
@require_POST
def send_message(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user != chat.customer and request.user != chat.shop.seller:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    data = json.loads(request.body)
    content = data.get('content')
    if not content:
        return JsonResponse({'error': 'Message content is required'}, status=400)
    
    message = Message.objects.create(
        chat=chat,
        sender=request.user,
        content=content,
        sent_at=timezone.now()
    )
    chat.is_read = False
    chat.save()
    
    return JsonResponse({
        'sender': message.sender.username,
        'content': message.content,
        'sent_at': message.sent_at.isoformat(),
        'is_read': message.is_read
    })




def seller_dashboard(request):
    return render(request, 'seller/dashboard.html')









def signup_view(request):
    if request.user.is_authenticated:
        return redirect('shop:home')

    if request.method == 'POST':
        # get input values
        f_name = request.POST.get('f-name', '').strip()
        l_name = request.POST.get('l-name', '').strip()
        email = request.POST.get('signup-email', '').strip()
        username = request.POST.get('signup-username', '').strip()
        password = request.POST.get('signup-password')
        re_pass = request.POST.get('re-pass')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone-number')
        account_type = request.POST.get('account-type')

        # validate
        if not all([f_name, l_name, email, password, re_pass]):
            messages.error(request, 'Please fill out all required fields.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        if password != re_pass:
            messages.error(request, 'Passwords do not match.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Email is already registered.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # create user
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=f_name,
            last_name=l_name,
            password=password,
            address=address,
            phone_number=phone_number,
            user_type = account_type
        )
        user.save()

        login(request, user)
        messages.success(request, 'Account created successfully!')

        # create seller shop if applicable
        if account_type == 'seller':
            Shop.objects.create(
                seller=user,
                name=f"{user.username}'s Shop",
                description="Welcome to my shop!"
            )
            return redirect('shop:seller_dashboard')

        return redirect('shop:products')

    return redirect('shop:home')

# def signup_view(request):
#     if request.user.is_authenticated:
#         return redirect('shop:home')
    
#     if request.method == 'POST':
#         form = SignupForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             if user.user_type == 'seller':
#                 Shop.objects.create(
#                     seller=user,
#                     name=f"{user.username}'s Shop",
#                     description="Welcome to my shop!"
#                 )
#             login(request, user)  # Auto-login after signup
#             return JsonResponse({'success': True, 'redirect': '/shop/'})
#         else:
#             return JsonResponse({'success': False, 'errors': form.errors}, status=400)
#     else:
#         form = SignupForm()
    
#     return render(request, 'shop/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        user = authenticate(request, username=user.username, password=password)
        if user:
            login(request, user)
            if request.user.user_type == 'seller':
                return redirect('shop:seller_dashboard')

            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            messages.error(request, 'Incorrect password.')
    return render(request, 'shop/home.html')

# def login_view(request):
#     if request.user.is_authenticated:
#         return redirect('shop:home')
    
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             user = authenticate(request, username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 return JsonResponse({'success': True, 'redirect': '/shop/'})
#             else:
#                 form.add_error(None, 'Invalid username or password')
#                 return JsonResponse({'success': False, 'errors': form.errors}, status=400)
#         else:
#             return JsonResponse({'success': False, 'errors': form.errors}, status=400)
#     else:
#         form = LoginForm()
    
#     return render(request, 'shop/login.html', {'form': form})

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('shop:home')
    return render(request, 'shop/home.html')



@login_required
def cart_view(request):
    if request.user.user_type != 'customer':
        return render(request, 'shop/cart.html', {'error': 'Only customers can access the cart'})
    
    cart, created = Cart.objects.get_or_create(customer=request.user)
    return render(request, 'shop/cart.html', {'cart': cart})

@login_required
@require_POST
def add_to_cart(request, product_id):
    if request.user.user_type != 'customer':
        return JsonResponse({'error': 'Only customers can add to cart'}, status=403)
    
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(customer=request.user)
    
    data = json.loads(request.body)
    # quantity = data.get('quantity', 1)  # Default to 1 if not provided
    quantity = 1
    form = CartItemForm({'quantity': quantity})
    
    if form.is_valid():
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': form.cleaned_data['quantity']}
        )
        if not created:
            cart_item.quantity += form.cleaned_data['quantity']
        if cart_item.quantity > product.stock:
            return JsonResponse({'error': 'Not enough stock available'}, status=400)
        if not product.is_available:
            return JsonResponse({'error': 'Product is not available'}, status=400)

        cart_item.save()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)

@login_required
@require_POST
def update_cart_item(request, cart_item_id):
    if request.user.user_type != 'customer':
        return JsonResponse({'error': 'Only customers can update cart'}, status=403)
    
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__customer=request.user)
    data = json.loads(request.body)
    form = CartItemForm(data)
    if form.is_valid():
        if form.cleaned_data['quantity'] > cart_item.product.stock:
            return JsonResponse({'error': 'Not enough stock available'}, status=400)
        cart_item.quantity = form.cleaned_data['quantity']
        cart_item.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)

@login_required
@require_POST
def delete_cart_item(request, cart_item_id):
    if request.user.user_type != 'customer':
        return JsonResponse({'error': 'Only customers can delete from cart'}, status=403)
    
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__customer=request.user)
    cart_item.delete()
    return JsonResponse({'success': True})

@login_required
@require_POST
def buy_now(request, product_id):
    if request.user.user_type != 'customer':
        return JsonResponse({'error': 'Only customers can buy products'}, status=403)
    
    product = get_object_or_404(Product, id=product_id, is_available=True)
    cart, created = Cart.objects.get_or_create(customer=request.user)
    
    # Clear existing cart items to ensure only the "Buy Now" product is included
    cart.items.all().delete()
    
    # Add the product to the cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
    else:
        cart_item.quantity = 1
    if cart_item.quantity > product.stock:
        return JsonResponse({'error': 'Not enough stock available'}, status=400)
    cart_item.save()
    
    return JsonResponse({'success': True, 'redirect': '/shop/checkout/'})

@login_required
def wishlist_view(request):
    if request.user.user_type != 'customer':
        return render(request, 'shop/wishlist.html', {'error': 'Only customers can access the wishlist'})

    wishlist, _ = Wishlist.objects.get_or_create(customer=request.user)
    wishlist_products = list(wishlist.products.all().order_by('-is_available', '-created_at').select_related('shop'))

    # Get cart product IDs for this user
    try:
        cart = Cart.objects.get(customer=request.user)
        cart_product_ids = set(cart.items.values_list('product_id', flat=True))
    except Cart.DoesNotExist:
        cart_product_ids = set()

    # Add `.is_in_cart` attribute for each product
    for product in wishlist_products:
        product.is_in_cart = product.id in cart_product_ids

    return render(request, 'shop/wishlist.html', {
        'wishlist_products_content': wishlist_products,
    })

@login_required
@require_POST
def add_to_wishlist(request, product_id):
    if request.user.user_type != 'customer':
        return JsonResponse({'error': 'Only customers can add to wishlist'}, status=403)
    
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(customer=request.user)
    wishlist.products.add(product)
    return JsonResponse({'success': True})

@login_required
@require_POST
def delete_from_wishlist(request, product_id):
    if request.user.user_type != 'customer':
        return JsonResponse({'error': 'Only customers can remove from wishlist'}, status=403)
    
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_object_or_404(Wishlist, customer=request.user)
    wishlist.products.remove(product)
    return JsonResponse({'success': True})

@login_required
def create_order(request):
    if request.user.user_type != 'customer':
        return JsonResponse({'error': 'Only customers can place orders'}, status=403)
    
    cart = get_object_or_404(Cart, customer=request.user)
    if not cart.items.exists():
        return JsonResponse({'error': 'Cart is empty'}, status=400)
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            shop_items = {}
            for item in cart.items.all():
                shop_items.setdefault(item.product.shop, []).append(item)
            
            for shop, items in shop_items.items():
                total_amount = sum(item.quantity * item.product.price for item in items)
                order = Order.objects.create(
                    customer=request.user,
                    shop=shop,
                    total_amount=total_amount,
                    shipping_address=form.cleaned_data['shipping_address'],
                    status='pending'
                )
                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        unit_price=item.product.price,
                        subtotal=item.quantity * item.product.price
                    )
                    item.product.stock -= item.quantity
                    item.product.save()
                    item.delete()
            
            return JsonResponse({'success': True, 'redirect': '/shop/orders/'})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = OrderForm()
    return render(request, 'shop/checkout.html', {'form': form, 'cart': cart})

@login_required
@require_POST
def cancel_order(request, order_id):
    if request.user.user_type != 'customer':
        return JsonResponse({'error': 'Only customers can cancel orders'}, status=403)
    
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    if order.status not in ['pending', 'processing']:
        return JsonResponse({'error': 'Order cannot be cancelled'}, status=400)
    
    order.status = 'cancelled'
    order.save()
    for item in order.items.all():
        item.product.stock += item.quantity
        item.product.save()
    return JsonResponse({'success': True})

@login_required
def reviews_view(request):
    if request.user.user_type != 'customer':
        return render(request, 'shop/reviews.html', {'error': 'Only customers can view reviews'})
    
    reviews = Review.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'shop/reviews.html', {'reviews': reviews})

@login_required
@require_POST
def add_review(request, product_id):
    if request.user.user_type != 'customer':
        return JsonResponse({'error': 'Only customers can add reviews'}, status=403)
    
    product = get_object_or_404(Product, id=product_id)
    data = json.loads(request.body)
    form = ReviewForm(data)
    if form.is_valid():
        review, created = Review.objects.update_or_create(
            product=product,
            customer=request.user,
            defaults={
                'rating': form.cleaned_data['rating'],
                'comment': form.cleaned_data['comment']
            }
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)

@login_required
@require_POST
def update_review(request, review_id):
    if request.user.user_type != 'customer':
        return JsonResponse({'error': 'Only customers can update reviews'}, status=403)
    
    review = get_object_or_404(Review, id=review_id, customer=request.user)
    data = json.loads(request.body)
    form = ReviewForm(data)
    if form.is_valid():
        review.rating = form.cleaned_data['rating']
        review.comment = form.cleaned_data['comment']
        review.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)

@login_required
@require_POST
def delete_review(request, review_id):
    if request.user.user_type != 'customer':
        return JsonResponse({'error': 'Only customers can delete reviews'}, status=403)
    
    review = get_object_or_404(Review, id=review_id, customer=request.user)
    review.delete()
    return JsonResponse({'success': True})

def products_view(request):
    # Annotate each product's shop with its follower count
    products = Product.objects.select_related('shop', 'shop__seller').annotate(
        follower_count=Count('shop__followers', distinct=True)
    ).order_by('-is_available', '-created_at')

    cart = None
    cart_product_ids = []

    if request.user.is_authenticated and request.user.user_type == 'customer':
        cart, _ = Cart.objects.get_or_create(customer=request.user)
        cart_product_ids = list(cart.items.values_list('product_id', flat=True))
    
    # Attach is_in_cart to each product
    for product in products:
        product.is_in_cart = product.id in cart_product_ids

    return render(request, 'shop/products.html', {
        'products': products,
        'cart': cart
    })

def search_products_ajax(request):
    search_query = request.GET.get('q', '')
    
    products = Product.objects.select_related('shop', 'shop__seller').annotate(
        follower_count=Count('shop__followers', distinct=True)
    )

    if search_query:
        products = products.filter(name__icontains=search_query)

    results = []
    for product in products:
        results.append({
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'description': product.description,
            'image': product.image.url if product.image else '/static/images/placeholder.jpg',
            'shop_name': product.shop.name,
            # 'shop_rating': product.shop.seller.rating or 0,
            # 'shop_products': product.shop.products.count(),
            # 'shop_followers': product.shop.followers.count(),
            # 'shop_id': product.shop.id,
            # 'rating': product.rating or 4.6,
            'products_sold': product.shop.products_sold or 0,
            'is_available': product.is_available,
        })
        
    return JsonResponse({'products': results})


@login_required
def product_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    form = OrderForm(initial={'shipping_address': request.user.address})
    review_form = ReviewForm()
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
        'review_form': review_form
    })

@login_required
@require_POST
def order_product_view(request, product_id):
    if request.user.user_type != 'customer':
        return JsonResponse({'error': 'Only customers can place orders'}, status=403)
    
    product = get_object_or_404(Product, id=product_id, is_available=True)
    data = json.loads(request.body)
    quantity = data.get('quantity', 1)
    if quantity < 1:
        return JsonResponse({'error': 'Quantity must be at least 1'}, status=400)
    if quantity > product.stock:
        return JsonResponse({'error': 'Not enough stock available'}, status=400)
    
    form = OrderForm(data)
    if form.is_valid():
        order = Order.objects.create(
            customer=request.user,
            shop=product.shop,
            total_amount=product.price * quantity,
            shipping_address=form.cleaned_data['shipping_address'],
            status='pending'
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=product.price,
            subtotal=product.price * quantity
        )
        product.stock -= quantity
        product.save()
        return JsonResponse({'success': True, 'redirect': '/shop/orders/'})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
def seller_dashboard_view(request):
    if request.user.user_type != 'seller':
        return render(request, 'shop/seller_dashboard.html', {'error': 'Unauthorized access'})

    shop, created = Shop.objects.get_or_create(
        seller=request.user,
        defaults={'name': f"{request.user.get_full_name() or request.user.username}'s Shop"}
    )

    # Global metrics
    total_listed_items = Product.objects.filter(shop=shop).count()
    available_stock = Product.objects.filter(shop=shop, is_available=True).aggregate(
        total=Sum('stock')
    )['total'] or 0

    all_time_revenue = OrderItem.objects.filter(
        order__shop=shop,
        order__status='completed'
    ).aggregate(total=Sum('subtotal'))['total'] or 0

    # Orders data for JS
    orders = Order.objects.filter(shop=shop).prefetch_related('items__product').order_by('-created_at')

    orders_data = []
    for order in orders:
        first_item = order.items.first()
        product_type = ""
        if first_item and first_item.product:
            product_type = first_item.product.type

        customer_pic = ""
        if order.customer.profile_picture and order.customer.profile_picture.name:
            customer_pic = settings.MEDIA_URL + order.customer.profile_picture.name.lstrip('/')

        # Or if .name is unreliable, fallback to string extraction (works with your current output)
        else:
            field_str = str(order.customer.profile_picture)
            if 'None' not in field_str and ':' in field_str:
                path = field_str.split(':', 1)[1].strip().rstrip('>')
                if path:
                    customer_pic = settings.MEDIA_URL + path.lstrip('/')

        orders_data.append({
            'id': order.id,
            'order_number': order.order_number,
            'created_at': order.created_at.isoformat(),
            'status': order.status,
            'total_amount': float(order.total_amount),
            'delivery_fee': float(order.delivery_fee),
            'tax': float(order.tax),
            'estimated_time_arrival': order.estimated_time_arrival or "",
            'customer_pic': customer_pic,
            'customer_name': order.customer.get_full_name(),
            'customer_id': order.customer.id,
            'product_name': first_item.product.name if first_item and first_item.product else "Unknown",
            'product_image': first_item.product.image.url if first_item and first_item.product and first_item.product.image else "",
            'unit_price': float(first_item.unit_price) if first_item else 0.0,
            'product_type': product_type,
        })

        print('orders_data', orders_data, order.customer.profile_picture)

    # Current year
    today = date.today()
    current_year = today.year

    # Full January to December months
    months = [(m, date(current_year, m, 1).strftime('%B')) for m in range(1, 13)]

    # Weeks from January to December 2025 (full year, starting from January)
    weeks = []
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December']

    current_year = date.today().year  # 2025

    # Start from first day of January
    start_date = date(current_year, 1, 1)

    # Find first Monday of the year
    monday = start_date - timedelta(days=start_date.weekday())

    # Generate all weeks in 2025
    while monday.year <= current_year:
        if monday.year == current_year:
            month_idx = monday.month - 1
            label = f"Week of {monday.strftime('%B %d, %Y')}"
            weeks.append((monday.isoformat(), label))
        monday += timedelta(days=7)

    context = {
        'shop': shop,
        'available_stock': available_stock,
        'total_listed_items': total_listed_items,
        'total_revenue': all_time_revenue,
        'products': Product.objects.filter(shop=shop).order_by('-created_at'),

        'orders_data': orders_data,
        'months': months,
        'weeks': weeks,
        'current_year': current_year,
    }

    return render(request, 'seller/dashboard.html', context)

@login_required
def admin_orders_view(request):
    if request.user.user_type != 'seller':
        return render(request, 'seller/edit_shop.html', {'error': 'Only sellers can access this page.'})

    # Get seller's shop and related orders
    seller_shop = get_object_or_404(Shop, seller=request.user)
    seller_orders = Order.objects.filter(
        items__product__shop=seller_shop
    ).distinct().order_by('-created_at')

    # Group orders by status
    grouped_orders = {
        'pending': seller_orders.filter(status='pending'),
        'shipped': seller_orders.filter(status='shipped'),
        'completed': seller_orders.filter(status='completed'),
        'cancelled': seller_orders.filter(status='cancelled'),
    }

    if request.method == 'POST':
        order = get_object_or_404(Order, id=request.POST.get('selected-id'))

        if 'cancel-order' in request.POST:
            order.status = 'cancelled'
            order.save()

            Notification.objects.create(
                user=order.customer,
                title="Order Cancelled",
                content=f"Your order #{order.order_number} has been cancelled by the seller.",
                type='order'
            )
            Notification.objects.create(
                user=request.user,
                title="Order Cancelled",
                content=f"Customer {order.customer.get_full_name()} order #{order.order_number} has been cancelled successfully.",
                type='order'
            )
            messages.success(request, f"Order #{order.order_number} has been cancelled.")
            return redirect('shop:admin_orders')

        elif 'approve-order' in request.POST:
            order.status = 'shipped'
            order.save()

            seller_shop.products_sold = seller_shop.products_sold + 1
            seller_shop.save()

            Notification.objects.create(
                user=order.customer,
                title="Order Approved",
                content=f"Your order #{order.order_number} has been approved and marked as shipped.",
                type='order'
            )
            Notification.objects.create(
                user=request.user,
                title="Order Approved",
                content=f"Customer {order.customer.get_full_name()} order #{order.order_number} has been approved successfully.",
                type='order'
            )
            messages.success(request, f"Order #{order.order_number} has been approved and marked as shipped.")
            return redirect('shop:admin_orders')

        elif 'complete-order' in request.POST:
            order.status = 'completed'
            order.save()

            Notification.objects.create(
                user=order.customer,
                title="Order Completed",
                content=f"Your order #{order.order_number} has been marked as completed by the seller.",
                type='order'
            )
            Notification.objects.create(
                user=request.user,
                title="Order Completed",
                content=f"Customer {order.customer.get_full_name()} order #{order.order_number} has been completed successfully.",
                type='order'
            )
            messages.success(request, f"Order #{order.order_number} marked as completed.")
            return redirect('shop:admin_orders')

    return render(request, 'list_of_orders.html', {'orders': grouped_orders})

@login_required
def admin_notifications_view(request):
    if request.user.user_type != 'seller':
        return render(request, 'seller/edit_shop.html', {'error': 'Only sellers can access this page.'})

    # Fetch notifications for the seller, ordered by newest first
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'seller/notifications.html', {
        'notifications': notifications
    })

@login_required
def edit_shop_view(request):
    if request.user.user_type != 'seller':
        return render(request, 'seller/edit_shop.html', {'error': 'Only sellers can edit shop details'})
    
    shop = get_object_or_404(Shop, seller=request.user)
    if request.method == 'POST':
        form = ShopForm(request.POST, instance=shop)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'redirect': '/shop/seller/dashboard/'})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = ShopForm(instance=shop)
    return render(request, 'seller/edit_shop.html', {'form': form, 'shop': shop})

@login_required
def seller_products_view(request):
    if request.user.user_type != 'seller':
        return render(request, 'shop/seller_products.html', {'error': 'Only sellers can view products'})
    
    shop = get_object_or_404(Shop, seller=request.user)
    products = Product.objects.filter(shop=shop).order_by('-is_available', '-created_at')
    return render(request, 'seller/products.html', {
        'shop': shop,
        'products': products,
    })

@login_required
def add_product_view(request):
    if request.user.user_type != 'seller':
        return render(request, 'seller/edit_product.html', {'error': 'Only sellers can add products'})

    shop = get_object_or_404(Shop, seller=request.user)

    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        description = request.POST.get('description', '').replace('\r\n', '\n').strip()
        material = request.POST.get('material')
        type_ = request.POST.get('type')
        image = request.FILES.get('image')

        # Validate required fields
        if not all([name, price, description, material, type_]):
            messages.error(request,  'All fields are required.')
            return redirect('shop:add_product')

        product = Product.objects.create(
            shop=shop,
            name=name,
            price=price,
            description=description,
            material=material,
            type=type_,
            image=image
        )

        return redirect('shop:seller_products')

    return render(request, 'seller/create_edit_product.html')

@login_required
def product_info_view(request, product_id):
    if request.user.user_type != 'seller':
        return render(request, 'seller/edit_product.html', {'error': 'No customers allowed'})

    product = get_object_or_404(Product, id=product_id, shop__seller=request.user)

    if request.method == 'POST':
        if 'mark-unavailable' in request.POST:
            product.is_available = False
            product.save()

            # Remove the product from all customer carts (excluding the seller if ever they had it)
            cart_items = CartItem.objects.filter(product=product)
            for cart_item in cart_items:
                customer = cart_item.cart.customer
                # Notify customer
                Notification.objects.create(
                    user=customer,
                    title="Product Unavailable",
                    content=f"'{product.name}' has been marked as unavailable by the seller and removed from your cart.",
                    type='product'
                )
                # Remove item from their cart
                cart_item.delete()

            messages.success(request, 'Product successfully marked as unavailable and removed from all customer carts.')

        elif 'mark-available' in request.POST:
            product.is_available = True
            product.save()

            messages.success(request, 'Product successfully marked as available.')

    return render(request, 'seller/product_info.html', {'product': product})

@login_required
def edit_product_view(request, product_id):
    if request.user.user_type != 'seller':
        return render(request, 'seller/edit_product.html', {'error': 'Only sellers can edit products'})

    product = get_object_or_404(Product, id=product_id, shop__seller=request.user)

    if request.method == 'POST':
        if 'save-edit' in request.POST:
            # Update product fields
            product.name = request.POST.get('name', product.name)
            product.price = request.POST.get('price', product.price)
            product.description = request.POST.get('description', product.description).replace('\r\n', '\n').strip()
            product.material = request.POST.get('material', product.material)
            product.type = request.POST.get('type', product.type)
            image = request.FILES.get('image')
            if image:
                product.image = image
            product.save()

            messages.success(request, 'Item info updated successfully.')
            return redirect('shop:product_info', product.id)

        elif 'delete' in request.POST:
            # Notify and remove from carts
            cart_items = CartItem.objects.filter(product=product)
            for cart_item in cart_items:
                Notification.objects.create(
                    user=cart_item.cart.customer,
                    title="Product Removed",
                    content=f"The item '{product.name}' has been removed by the seller and was removed from your cart.",
                    type='product'
                )
                cart_item.delete()

            product.delete()
            messages.success(request, 'Product deleted successfully and removed from customer carts.')
            return redirect('shop:seller_products')

    return render(request, 'seller/create_edit_product.html', {'product': product})

@login_required
@require_POST
def delete_product_view(request, product_id):
    if request.user.user_type != 'seller':
        return render(request, 'seller/seller_products.html', {'error': 'Only sellers can delete products'})
    
    product = get_object_or_404(Product, id=product_id, shop__seller=request.user)
    product.delete()
    return redirect('shop:seller_products')

# @login_required
# @require_POST
# def delete_product_view(request, product_id):
#     if request.user.user_type != 'seller':
#         return JsonResponse({'error': 'Only sellers can delete products'}, status=403)
    
#     product = get_object_or_404(Product, id=product_id, shop__seller=request.user)
#     product.delete()
#     return JsonResponse({'success': True})

@login_required
@require_POST
def update_order_view(request, order_id):
    if request.user.user_type != 'seller':
        return JsonResponse({'error': 'Only sellers can update orders'}, status=403)
    
    order = get_object_or_404(Order, id=order_id, shop__seller=request.user)
    data = json.loads(request.body)
    status = data.get('status')
    if status not in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        return JsonResponse({'error': 'Invalid status'}, status=400)
    
    order.status = status
    order.save()
    return JsonResponse({'success': True})

@login_required
def seller_categories_view(request):
    if request.user.user_type != 'seller':
        return render(request, 'seller/seller_categories.html', {'error': 'Only sellers can view categories'})

    shop = get_object_or_404(Shop, seller=request.user)

    # Get all categories that have at least one product for this shop
    categories = Category.objects.filter(products__shop=shop).distinct().order_by('name')

    # Dictionary of categories with their products (shop-specific)
    category_products = {
        category: category.products.filter(shop=shop).order_by('name')
        for category in categories
    }

    return render(request, 'seller/seller_categories.html', {
        'shop': shop,
        'category_products': category_products,
    })

@login_required
def create_category_view(request):
    if request.user.user_type != 'seller':
        return render(request, 'seller/category_form.html', {'error': 'Only sellers can manage categories'})
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('shop:seller_categories')
    else:
        form = CategoryForm()
    
    return render(request, 'seller/category_form.html', {'form': form, 'action': 'Create'})

@login_required
def edit_category_view(request, category_id):
    if request.user.user_type != 'seller':
        return render(request, 'seller/category_form.html', {'error': 'Only sellers can manage categories'})
    
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('shop:seller_categories')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'seller/category_form.html', {'form': form, 'action': 'Edit'})

@login_required
@require_POST
def delete_category_view(request, category_id):
    if request.user.user_type != 'seller':
        return render(request, 'seller/seller_categories.html', {'error': 'Only sellers can manage categories'})

    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return redirect('shop:seller_categories')



@login_required
def profile(request):
    user = request.user

    if request.method == 'POST':
        # === Profile Picture Upload (always check if file was uploaded) ===
        if 'profile' in request.FILES:
            user.profile_picture = request.FILES['profile']

        # === Update Basic Profile Info ===
        user.first_name = request.POST.get('f-name', '').strip()
        user.middle_name = request.POST.get('m-name', '').strip()
        user.last_name = request.POST.get('l-name', '').strip()
        user.address = request.POST.get('address', '').strip()
        user.phone_number = request.POST.get('phone-number', '').strip()

        # === Change Password (only if triggered from password modal) ===
        if 'change-password' in request.POST:
            old_password = request.POST.get('old-password')
            new_password = request.POST.get('password')
            confirm_password = request.POST.get('re-pass')

            if not user.check_password(old_password):
                messages.error(request, "Old password is incorrect.")
            elif new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
            elif len(new_password) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
            else:
                user.set_password(new_password)
                update_session_auth_hash(request, user)  # Keeps user logged in
                messages.success(request, "Password changed successfully!")

        # === Save everything (info + picture + password if changed) ===
        user.save()

        # Success message (covers both save-info and password change)
        if 'change-password' not in request.POST:
            messages.success(request, "Profile updated successfully!")

        return redirect('shop:profile')

    # GET request - just show the profile page
    return render(request, 'profile.html', {'user': user})


def generate_unique_order_number():
    """Generate a unique order number"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ORD-{timestamp}-{random_str}"

def generate_reference_number():
    """Generate a unique payment reference number"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.digits, k=6))
    return f"GC-{timestamp}-{random_str}"

@login_required
def checkout(request):
    try:
        cart = request.user.cart
    except AttributeError:
        messages.error(request, "You do not have a cart.")
        return redirect('shop:products')

    items = cart.items.select_related('product__shop').all()
    if not items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('shop:products')

    # Group items by shop to determine unique sellers
    items_by_shop = defaultdict(list)
    for item in items:
        items_by_shop[item.product.shop].append(item)

    unique_sellers = len(items_by_shop)
    delivery_fee_per_seller = Decimal('159.00')
    total_delivery_fee = unique_sellers * delivery_fee_per_seller

    # Calculate subtotal
    subtotal = sum(Decimal(str(item.product.price)) * item.quantity for item in items)

    # 5% tax on subtotal
    tax = (subtotal * Decimal('0.05')).quantize(Decimal('0.01'))

    # Final total
    total = subtotal + total_delivery_fee + tax

    # Total quantity of items
    total_items = sum(item.quantity for item in items)

    # Estimated arrival (6-8 days from today)
    today = datetime.today()
    eta_start = today + timedelta(days=6)
    eta_end = today + timedelta(days=8)
    eta_range = f"{eta_start.strftime('%B %d')} - {eta_end.strftime('%d, %Y')}"

    if request.method == 'POST':
        mop = request.POST.get('mop', 'cod').lower()

        if mop == 'gcash':
            reference_number = generate_reference_number()

            cart_data = [{
                'product_id': ci.product.id,
                'quantity': ci.quantity,
                'price': float(ci.product.price),
                'shop_id': ci.product.shop.id,
            } for ci in items]

            payment = Payment.objects.create(
                customer=request.user,
                reference_number=reference_number,
                amount=total,
                payment_method='gcash',
                status='pending',
                session_data={
                    'cart_data': cart_data,
                    'unique_sellers': unique_sellers,
                    'delivery_fee_per_seller': float(delivery_fee_per_seller),
                    'tax': float(tax),
                    'eta_range': eta_range,
                }
            )

            paymongo = PayMongoAPI()
            amount_in_cents = int(total * 100)

            success_url = request.build_absolute_uri(
                reverse('shop:gcash_callback') + f'?payment_id={payment.id}'
            )
            failed_url = request.build_absolute_uri(
                reverse('shop:gcash_failed') + f'?payment_id={payment.id}'
            )

            result = paymongo.create_source(
                amount=amount_in_cents,
                description=f"Order payment - {reference_number}",
                redirect_success=success_url,
                redirect_failed=failed_url
            )

            if result['success']:
                source_data = result['data']['data']
                payment.source_id = source_data['id']
                payment.checkout_url = source_data['attributes']['redirect']['checkout_url']
                payment.save()

                return JsonResponse({
                    'success': True,
                    'checkout_url': payment.checkout_url,
                })
            else:
                # Better error reporting
                error_msg = result.get('error', 'Unknown error')
                response_data = result.get('response', {})
                payment.status = 'failed'
                payment.save()

                return JsonResponse({
                    'success': False,
                    'message': f'Payment failed: {error_msg}',
                    'details': response_data
                }, status=400)
    
        elif mop == 'cod':
            return process_cod_order(
                request=request,
                items=items,
                delivery_fee_per_seller=delivery_fee_per_seller,
                eta_range=eta_range
            )

    return render(request, 'customer/checkout.html', {
        'cart': cart,
        'total_items': total_items,
        'subtotal': subtotal,
        'unique_sellers': unique_sellers,
        'delivery_fee_per_seller': delivery_fee_per_seller,
        'total_delivery_fee': total_delivery_fee,
        'tax': tax,
        'total': total,
        'eta_range': eta_range,
    })

@login_required
def gcash_callback(request):
    payment_id = request.GET.get('payment_id')
    
    if not payment_id:
        messages.error(request, "Invalid payment session.")
        return redirect('shop:products')
    
    try:
        payment = Payment.objects.get(id=payment_id, customer=request.user)
    except Payment.DoesNotExist:
        messages.error(request, "Payment not found.")
        return redirect('shop:products')
    
    paymongo = PayMongoAPI()
    source_result = paymongo.retrieve_source(payment.source_id)
    
    if not source_result['success']:
        payment.status = 'failed'
        payment.save()
        messages.error(request, "Failed to verify payment.")
        return redirect('shop:products')
    
    source_data = source_result['data']['data']
    source_status = source_data['attributes']['status']
    
    if source_status == 'chargeable':
        # Create payment to charge the source
        amount_in_cents = int(payment.amount * 100)
        payment_result = paymongo.create_payment(
            source_id=payment.source_id,
            amount=amount_in_cents,
            description=f"Order payment - {payment.reference_number}"
        )
        
        if payment_result['success']:
            payment_data = payment_result['data']['data']
            payment.payment_id = payment_data['id']
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            payment.save()
            
            # === IMPORTANT: Create Orders from session data ===
            session_data = payment.session_data
            cart_data = session_data.get('cart_data', [])
            delivery_fee_per_seller = Decimal(str(session_data.get('delivery_fee_per_seller', 159)))
            tax_rate = Decimal('0.05')
            eta_range = session_data.get('eta_range', "Within 6-8 days")
            
            # Group by shop
            items_by_shop = defaultdict(list)
            for item in cart_data:
                product = Product.objects.get(id=item['product_id'])
                items_by_shop[product.shop].append({
                    'product': product,
                    'quantity': item['quantity'],
                    'price': Decimal(str(item['price']))
                })
            
            with transaction.atomic():
                for shop, shop_items in items_by_shop.items():
                    subtotal = sum(item['price'] * item['quantity'] for item in shop_items)
                    tax = (subtotal * tax_rate).quantize(Decimal('0.01'))
                    total_amount = subtotal + delivery_fee_per_seller + tax
                    
                    order = Order.objects.create(
                        customer=request.user,
                        shop=shop,
                        order_number=generate_unique_order_number(),
                        delivery_fee=delivery_fee_per_seller,
                        tax=tax,
                        total_amount=total_amount,
                        estimated_time_arrival=eta_range,
                        mode_of_payment='gcash',
                        status='pending'
                    )
                    
                    for item in shop_items:
                        for _ in range(item['quantity']):
                            OrderItem.objects.create(
                                order=order,
                                product=item['product'],
                                quantity=1,
                                unit_price=item['price'],
                                subtotal=item['price']
                            )
                        
                        # Make product unavailable
                        item['product'].is_available = False
                        item['product'].save()
                        
                        # Remove from other carts
                        other_cart_items = CartItem.objects.filter(product=item['product']).exclude(cart__customer=request.user)
                        for other in other_cart_items:
                            if other.cart and other.cart.customer:
                                Notification.objects.create(
                                    user=other.cart.customer,
                                    title="Item no longer available",
                                    content=f"'{item['product'].name}' was purchased by another customer.",
                                    type='product'
                                )
                            other.delete()
                    
                    # Notify seller
                    Notification.objects.create(
                        user=shop.seller,
                        title="New GCash Order",
                        content=f"New order #{order.order_number} worth ₱{total_amount}",
                        type='order'
                    )
                
                # Notify buyer
                Notification.objects.create(
                    user=request.user,
                    title="Order Placed",
                    content=f"Your GCash order(s) placed. Estimated arrival: {eta_range}.",
                    type='order'
                )
            
            # Clear cart
            request.user.cart.items.all().delete()
            
            messages.success(request, "Payment successful! Your order has been placed.")
            return redirect('shop:checkout_success')
        else:
            payment.status = 'failed'
            payment.save()
            messages.error(request, "Payment failed.")
            return redirect('shop:products')
    
    elif source_status == 'pending':
        messages.info(request, "Payment still processing.")
        return redirect('shop:products')
    
    else:
        payment.status = 'failed'
        payment.save()
        messages.error(request, "Payment not authorized.")
        return redirect('shop:products')
    
@login_required
def gcash_failed(request):
    """Handle GCash authorization failure"""
    payment_id = request.GET.get('payment_id')
    
    if payment_id:
        try:
            payment = Payment.objects.get(id=payment_id, customer=request.user)
            payment.status = 'failed'
            payment.save()
        except Payment.DoesNotExist:
            pass
    
    messages.error(request, "Payment was cancelled or failed. Please try again.")
    return redirect('shop:products')

def process_order_from_payment(payment):
    """Process order after successful payment"""
    session_data = payment.session_data
    cart_data = session_data.get('cart_data', [])
    delivery_fee_per_item = session_data.get('delivery_fee_per_item', 200)
    eta_range = session_data.get('eta_range', '')
    
    # Create orders from cart data
    for item_data in cart_data:
        try:
            product = Product.objects.get(id=item_data['product_id'])
            
            if not product.is_available:
                continue
            
            for _ in range(item_data['quantity']):
                order_number = generate_unique_order_number()
                
                order = Order.objects.create(
                    customer=payment.customer,
                    shop_id=item_data['shop_id'],
                    order_number=order_number,
                    delivery_fee=delivery_fee_per_item,
                    total_amount=item_data['price'] + delivery_fee_per_item,
                    estimated_time_arrival=eta_range,
                    mode_of_payment='Gcash',
                    payment_reference=payment.reference_number
                )
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=1,
                    unit_price=item_data['price'],
                    subtotal=item_data['price']
                )
                
                product.is_available = False
                product.save()
                
                # Remove from other carts
                other_carts = CartItem.objects.filter(
                    product=product
                ).exclude(cart__customer=payment.customer)
                
                for other_item in other_carts:
                    if other_item.cart and other_item.cart.customer:
                        Notification.objects.create(
                            user=other_item.cart.customer,
                            title="Item removed",
                            content=f"'{product.name}' has been ordered by another customer and removed from your cart.",
                            type='product'
                        )
                    other_item.delete()
                
                # Notify seller
                Notification.objects.create(
                    user=product.shop.seller,
                    title="New order",
                    content=f"You have a new order for '{product.name}'!",
                    type='order'
                )
        
        except Product.DoesNotExist:
            continue
    
    # Clear cart
    try:
        cart = payment.customer.cart
        cart.items.all().delete()
    except:
        pass
    
    # Notify buyer
    Notification.objects.create(
        user=payment.customer,
        title="Payment successful",
        content=f"Your GCash payment of ₱{payment.amount} has been processed successfully!",
        type='order'
    )

def process_cod_order(request, items, delivery_fee_per_seller, eta_range=None):
    """Process Cash on Delivery order - one Order per seller"""
    cart = request.user.cart
    eta_range = eta_range or "Within 6-8 days"
    tax_rate = Decimal('0.05')

    # Group items by shop
    items_by_shop = defaultdict(list)
    for cart_item in items:
        items_by_shop[cart_item.product.shop].append(cart_item)

    with transaction.atomic():
        for shop, shop_items in items_by_shop.items():
            subtotal = sum(Decimal(str(ci.product.price)) * ci.quantity for ci in shop_items)
            tax = (subtotal * tax_rate).quantize(Decimal('0.01'))
            total_amount = subtotal + Decimal(str(delivery_fee_per_seller)) + tax

            order = Order.objects.create(
                customer=request.user,
                shop=shop,
                order_number=generate_unique_order_number(),
                delivery_fee=delivery_fee_per_seller,
                tax=tax,
                total_amount=total_amount,
                estimated_time_arrival=eta_range,
                mode_of_payment='cod',
                status='pending'
            )

            for cart_item in shop_items:
                for _ in range(cart_item.quantity):
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=1,
                        unit_price=cart_item.product.price,
                        subtotal=cart_item.product.price
                    )

                cart_item.product.is_available = False
                cart_item.product.save()

                # Remove from other carts
                other_cart_items = CartItem.objects.filter(product=cart_item.product).exclude(cart=cart)
                for other_item in other_cart_items:
                    if other_item.cart and other_item.cart.customer:
                        Notification.objects.create(
                            user=other_item.cart.customer,
                            title="Item no longer available",
                            content=f"'{cart_item.product.name}' was purchased by another customer.",
                            type='product'
                        )
                    other_item.delete()

            # Notify seller
            Notification.objects.create(
                user=shop.seller,
                title="New COD Order",
                content=f"New order #{order.order_number} worth ₱{total_amount}",
                type='order'
            )

        # Notify buyer once
        Notification.objects.create(
            user=request.user,
            title="Order Placed",
            content=f"Your COD order(s) placed. Estimated arrival: {eta_range}.",
            type='order'
        )

    cart.items.all().delete()
    messages.success(request, "Order placed successfully!")
    return redirect('shop:checkout_success')

@login_required
def checkout_success(request):
    return render(request, 'customer/checkout_success.html')

@require_POST
@login_required
def mark_notification_read(request):
    notif_id = request.POST.get("notif_id")
    try:
        notif = Notification.objects.get(id=notif_id, user=request.user)
        notif.is_read = True
        notif.save()
        return JsonResponse({"success": True})
    except Notification.DoesNotExist:
        return JsonResponse({"success": False, "error": "Notification not found"})

@login_required
def orders_view(request):
    if request.user.user_type != 'customer':
        return render(request, 'shop/orders.html', {'error': 'Only customers can view orders'})
        
    user_orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    grouped_orders = {
        'pending': [],
        'shipped': [],
        'completed': [],
        'cancelled': [],
    }

    for order in user_orders:
        # Check if user can rate
        has_completed_order = OrderItem.objects.filter(
            order__customer=request.user,
            order__status='completed',
            product__shop=order.shop
        ).exists()

        has_already_rated = ShopReview.objects.filter(customer=request.user, shop=order.shop).exists()
        order.can_rate_shop = has_completed_order and has_already_rated

        grouped_orders[order.status].append(order)

    # grouped_orders = {
    #     'pending': user_orders.filter(status='pending'),
    #     'shipped': user_orders.filter(status='shipped'),
    #     'completed': user_orders.filter(status='completed'),
    #     'cancelled': user_orders.filter(status='cancelled'),
    # }

    if request.method == 'POST':
        if 'cancel-order' in request.POST:
            order = get_object_or_404(Order, id=request.POST.get('selected-id'), customer=request.user)
            order.status = 'cancelled'
            order.save()

            # Notify the seller
            seller = order.shop.seller
            Notification.objects.create(
                user=seller,
                title="Order Cancelled",
                content=f"Your order #{order.id} from {request.user.get_full_name()} has been cancelled.",
                type='order'
            )

            messages.success(request, 'Order cancelled successfully!')
            return redirect('shop:orders')
        
        elif 'upload-gcash-receipt' in request.POST:
            order_id = request.POST.get('order_id')
            order = get_object_or_404(Order, id=order_id, customer=request.user, mode_of_payment='gcash')
            
            receipt_file = request.FILES.get('gcash_receipt')
            if receipt_file:
                order.gcash_receipt = receipt_file
                order.save()
                
                # Notify seller
                Notification.objects.create(
                    user=order.shop.seller,
                    title="GCash Receipt Uploaded",
                    content=f"Customer {request.user.get_full_name()} uploaded GCash receipt for order #{order.order_number}.",
                    type='order'
                )
                
                messages.success(request, "GCash receipt uploaded successfully!")
            else:
                messages.error(request, "Please select an image to upload.")
            
            return redirect('shop:orders')


    return render(request, 'list_of_orders.html', {'orders': grouped_orders})

@login_required
def admin_list_of_users(request):
    if not request.user.is_superuser:
        return redirect('shop:home')  # Redirect non-admins

    all_users = User.objects.exclude(id=request.user.id)

    sellers = all_users.filter(user_type='seller')
    customers = all_users.filter(user_type='customer')

    if request.method == 'POST':
        user = get_object_or_404(User, id=request.POST.get('selected-id'))

        if 'ban-account' in request.POST:
            user.is_active = False
            user.save()

            Notification.objects.create(
                user=user,
                title="Account banned",
                content=f"Your account has been banned by the admin.",
                type='account'
            )
            Notification.objects.create(
                user=request.user,
                title="Account banned",
                content=f"Account {user.user_type} {user.get_full_name()} has been banned successfully.",
                type='account'
            )
            messages.success(request, f"Account {user.user_type} {user.get_full_name()} has been banned successfully.")

        elif 'activate-account' in request.POST:
            user.is_active = True
            user.save()

            Notification.objects.create(
                user=user,
                title="Account activated",
                content=f"Your account has been activated by the admin.",
                type='account'
            )
            Notification.objects.create(
                user=request.user,
                title="Account banned",
                content=f"Account {user.user_type} {user.get_full_name()} has been activated successfully.",
                type='account'
            )
            messages.success(request, f"Account {user.user_type} {user.get_full_name()} has been activated successfully.")

        return redirect('shop:list_of_users')

    return render(request, 'list_of_users.html', {
        'sellers': sellers,
        'customers': customers,
    })

def global_data(request):
    cart = None
    notifications = None
    chats = None
    cart_subtotal = 0
    wishlist_products = []
    orders_count = 0  # New: total orders received by seller

    if request.user.is_authenticated:
        # Cart, wishlist, notifications for customers
        if request.user.user_type == 'customer':
            cart, _ = Cart.objects.get_or_create(customer=request.user)
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

            # Cart subtotal
            if cart:
                cart_subtotal = sum(
                    item.product.price * item.quantity
                    for item in cart.items.select_related('product')
                )

            # Wishlist
            wishlist, _ = Wishlist.objects.get_or_create(customer=request.user)
            products = wishlist.products.all().select_related('shop')

            for product in products:
                wishlist_products.append({
                    'id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'image': product.image.url if product.image else '',
                    'shop_id': product.shop.id,
                    'material': product.get_material_display(),
                    'type': product.get_type_display(),
                    'is_in_cart': product.is_in_cart(request.user),
                })

        # Seller-specific data
        if request.user.user_type == 'seller' or request.user.is_staff:  # include admin if needed
            shop = Shop.objects.filter(seller=request.user).first()
            if shop:
                # Total orders received by this shop (from customers)
                orders_count = Order.objects.filter(shop=shop).count()

                # Chats and notifications for seller
                chats = Chat.objects.filter(shop=shop).order_by('created_at')
                notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

        # Common notifications count
        unread_notif_count = notifications.filter(is_read=False).count() if notifications else 0
        unread_chats_count = chats.filter(is_read=False).count() if chats else 0

    else:
        unread_notif_count = 0
        unread_chats_count = 0

    return {
        'cart': cart,
        'cart_subtotal': cart_subtotal,
        'wishlist_products': wishlist_products,
        'notifications': notifications,
        'unread_notif_count': unread_notif_count,
        'unread_chats_count': unread_chats_count,
        'orders_count': orders_count,  # ← New: available in all templates
    }


@login_required
def gcash_payment(request, session_id):
    payment_session = request.session.get('payment_session')
    
    if not payment_session or payment_session['session_id'] != session_id:
        messages.error(request, "Invalid payment session.")
        return redirect('shop:products')
    
    # Check if session is expired (10 minutes)
    created_at = datetime.fromisoformat(payment_session['created_at'])
    if datetime.now() - created_at > timedelta(minutes=10000):
        messages.error(request, "Payment session expired. Please try again.")
        del request.session['payment_session']
        return redirect('shop:checkout')
    
    context = {
        'session_id': session_id,
        'amount': payment_session['amount'],
        'merchant_name': 'Your Shop Name',
        'reference_number': f"REF{session_id[:8].upper()}",
    }
    
    return render(request, 'customer/gcash_payment.html', context)

@login_required
def process_gcash_payment(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

    session_id = request.POST.get('session_id')
    mobile_number = request.POST.get('mobile_number')
    mpin = request.POST.get('mpin')

    payment_session = request.session.get('payment_session')

    if not payment_session:
        return JsonResponse({'success': False, 'message': 'No payment session found. Please start checkout again.'})

    if payment_session['session_id'] != session_id:
        return JsonResponse({'success': False, 'message': 'Invalid payment session ID.'})

    try:
        created_at = datetime.fromisoformat(payment_session['created_at'])
        if (datetime.now() - created_at).total_seconds() > 900:  # 15 minutes
            if 'payment_session' in request.session:
                del request.session['payment_session']
            return JsonResponse({'success': False, 'message': 'Payment session expired. Please start checkout again.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Invalid session data.'})

    if not mobile_number or not mpin:
        return JsonResponse({'success': False, 'message': 'Mobile number and MPIN are required.'})

    try:
        time.sleep(2)  # Simulate payment processing
        if len(mobile_number) >= 11 and len(mpin) == 4:
            cart = Cart.objects.get(id=payment_session['cart_id'])
            delivery_fee_per_item = 200

            for item_data in payment_session['items']:
                product = Product.objects.get(id=item_data['product_id'])
                for _ in range(item_data['quantity']):
                    order = Order.objects.create(
                        customer=request.user,
                        shop_id=item_data['shop_id'],
                        total_amount=item_data['price'] + delivery_fee_per_item,
                        estimated_time_arrival=payment_session['eta_range'],
                        mode_of_payment='Gcash',
                        status='pending'
                    )
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=1,
                        unit_price=item_data['price'],
                        subtotal=item_data['price']
                    )
                    Payment.objects.create(
                        payment_intent_id=session_id,
                        order=order,
                        amount=item_data['price'] + delivery_fee_per_item,
                        status='completed',
                        payment_method='gcash'
                    )

            cart.items.all().delete()
            request.session['gcash_payment_success'] = True
            if 'payment_session' in request.session:
                del request.session['payment_session']

            return JsonResponse({
                'success': True,
                'redirect_url': reverse('shop:checkout_success')
            })
        else:
            return JsonResponse({'success': False, 'message': 'Invalid mobile number (must be 11+ digits) or MPIN (must be 4 digits)'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error processing payment: {str(e)}'})