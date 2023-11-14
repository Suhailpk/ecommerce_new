from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import *
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required

# Create your views here.

def home(request):
    if request.method == "GET":
        products = Product.objects.all()
        return render(request, 'index.html',{'products':products})
    
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories,is_available=True).order_by('id')
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 4)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)

        product_count = products.count()

    params = {
            'products':paged_products,
            'product_count':product_count,
            }
    return render(request, 'store/store.html',params)


def product_detail(request, category_slug, product_slug):
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        variations = Variation.objects.filter(product=product)
        print(variations)  # Check the variations in the console
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=product).exists()
    except Exception as e:
        raise e

    context = {"product": product, 'in_cart': in_cart}
    return render(request, 'store/product-detail.html', context)




def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()

    return cart

def cart(request,total=0,quantity=0,cart_items=None):
    tax = 0
    grand_total = 0
    try:
        
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True).order_by('id')
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('id')
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax

    except Cart.DoesNotExist:
        pass

        
    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,
    }
    return render(request, 'store/cart.html', context)


def add_to_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    
    if current_user.is_authenticated:
        if request.method == 'POST':
            product_variations = []
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variations.append(variation)
                except:
                    pass
            
        
        cart_item_exist = CartItem.objects.filter(product=product, user=current_user).exists()
        if cart_item_exist:
            cart_items = CartItem.objects.filter(product=product, user=current_user)

            existing_variation = []
            id = []
            

            for cart_item in cart_items:
                item_variation = cart_item.variation.all()
                existing_variation.append(list(item_variation))
                id.append(cart_item.id)


            if product_variations in existing_variation:

                index = existing_variation.index(product_variations)

                item_id = id[index]

                cart_item = CartItem.objects.get(product=product, id=item_id)
                cart_item.quantity += 1
                cart_item.save()
            else:
                cart_item = CartItem.objects.create(product=product, user=current_user, quantity=1)
                if len(product_variations) > 0:
                    cart_item.variation.clear()
                    cart_item.variation.add(*product_variations)
                cart_item.save()
                
        else:
            print('this else is working')
            cart_item = CartItem.objects.create(product=product, user=current_user, quantity=1)
            if len(product_variations) > 0:
                cart_item.variation.clear()
                cart_item.variation.add(*product_variations)
            cart_item.save()

        return redirect('cart')
    
    #if user is not authenitcated
    else:
        
        if request.method == 'POST':
            product_variations = []
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variations.append(variation)
                except:
                    pass
            
        
        try:
            cart = Cart.objects.get(cart_id = _cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id = _cart_id(request))
            cart.save() 

        cart_item_exist = CartItem.objects.filter(product=product, cart=cart).exists()
        if cart_item_exist:
            cart_items = CartItem.objects.filter(product=product, cart=cart)

            existing_variation = []
            id = []
            

            for cart_item in cart_items:
                item_variation = cart_item.variation.all()
                existing_variation.append(list(item_variation))
                id.append(cart_item.id)


            if product_variations in existing_variation:

                index = existing_variation.index(product_variations)

                item_id = id[index]

                cart_item = CartItem.objects.get(product=product, id=item_id)
                cart_item.quantity += 1
                cart_item.save()
            else:
                cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
                if len(product_variations) > 0:
                    cart_item.variation.clear()
                    cart_item.variation.add(*product_variations)
                cart_item.save()
                
        else:
            print('this else is working')
            cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
            if len(product_variations) > 0:
                cart_item.variation.clear()
                cart_item.variation.add(*product_variations)
            cart_item.save()

        return redirect('cart')

def decrement_cart_item(request, product_id, cart_item_id):
    
    product = Product.objects.get(id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product,user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product,cart=cart, id=cart_item_id)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass

    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    

    
    product = Product.objects.get(id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product,user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product,cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')
    

def cart_items_number(request,quantity=0):
    cart  = Cart.objects.get(cart_id=_cart_id(request))
    cart_items = CartItem.objects.filter(cart=cart)
    for cart_item in cart_items:
        quantity+= cart_item.quantity

    context = {
        'cart_quantity':quantity,
    }

    return render(request, 'includes/navbar.html', context)

    
def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
             products = Product.objects.order_by('-created_date').filter(Q(product_name__icontains=keyword)|Q(description__icontains=keyword))
             product_count = products.count()
    
    context = {
        'products':products,
        'product_count':product_count,
    }

    return render(request, 'store/store.html',context )



def dashboard(request):
    return render(request, 'dashboard.html')

@login_required(login_url='login')
def checkout(request, total=0,quantity=0,cart_items=None):
    tax = 0
    grand_total = 0
    try:
        # cart = Cart.objects.get(cart_id=_cart_id(request))
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True).order_by('id')
            for cart_item in cart_items:
                total += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity
            tax = (2 * total)/100
            grand_total = total + tax

    except Cart.DoesNotExist:
        pass

        
    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,
    }
    return render(request, 'store/checkout.html', context)







