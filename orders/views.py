from django.shortcuts import render, redirect
from django.http.response import JsonResponse
from store.models import CartItem, Product
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
import datetime
import json
from django.conf import settings
from django.core.mail import send_mail

# Create your views here.
def order(request, total=0,quantity=0):
    current_user = request.user
    cart_item = CartItem.objects.filter(user=current_user)
    cart_item_count = cart_item.count()
    if cart_item_count <= 0:
        return redirect('home')
    
    grand_total = 0
    tax = 0
    cart_items = CartItem.objects.filter(user=current_user)
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = tax + total
    
    
    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            print('here')
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.tax = tax
            data.order_total = grand_total
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            yr = int(datetime.date.today().strftime('%Y'))
            mt = int(datetime.date.today().strftime('%m'))
            dt = int(datetime.date.today().strftime('%d'))
            d = datetime.date(yr,mt,dt)

            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)

            context = {
                'order':order,
                'cart_items':cart_items,
                'tax':tax,
                'total':total,
                'grand_total':grand_total
            }

            return render(request, 'orders/payments.html', context)
        else:
            return redirect('checkout')
        

def payments(request):
    body  = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status']
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    #Save the details in OrderProduct table
    cart_items = CartItem.objects.filter(user=request.user)
    for cart_item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.user = request.user
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.product_id = cart_item.product.id
        orderproduct.quantity = cart_item.quantity
        orderproduct.product_price = cart_item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=cart_item.id)
        cart_item_variation = cart_item.variation.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(cart_item_variation)
        orderproduct.save()

        #Reduce  the stock in products
        product = Product.objects.get(id=cart_item.product.id)
        product.stock -= cart_item.quantity
        product.save()

    #clear the cart item
    CartItem.objects.filter(user=request.user).delete()


    #Send the mail product invoice
    def send_mail_for_product_invoice(email):
        subject = f'Thank for purachasing'
        message = f'Sample invoice'
        from_mail = settings.EMAIL_HOST_USER


        send_mail(
            subject=subject,
            message=message,
            from_email=from_mail,
            recipient_list=[email]
            )
        
    send_mail_for_product_invoice(email=request.user.email)

    data = {
        'order_number':order.order_number,
        'TransID':payment.payment_id
    }

    return JsonResponse(data)


    


def order_complete(request):
    order_number = request.GET.get('order_number')
    transid = request.GET.get('payment_id')

    print('order_number============= ' ,order_number)
    print('transid================ ' ,transid)


    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        print('order_product=================', ordered_products)

        payment = Payment.objects.get(payment_id=transid)

        total = 0
        for item in ordered_products:
            total += item.product_price * item.quantity
            
        tax = order.tax
        grand_total = order.order_total

        context = {
            'order':order,
            'ordered_products':ordered_products,
            'order_number':order.order_number,
            'payment':payment,
            'total':total,
            'tax':tax,
            'grand_total':grand_total,
        }

        return render(request, 'orders/order_complete.html',context)
    except(Order.DoesNotExist, OrderProduct.DoesNotExist):
        return redirect('order_complete')

    




            
        
    
    
