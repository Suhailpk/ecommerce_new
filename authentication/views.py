from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Profile
import uuid
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.contrib import messages
from accounts.models import Account
from django.contrib.auth.hashers import check_password
from store.views import _cart_id
from store.models import Cart, CartItem
import requests


# Create your views here.



def login_page(request):
    if request.method == "GET":
        return render(request, 'signin.html')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Check if the user exists
        user_obj = Account.objects.filter(email=email).first()
        print('user_obj===========', user_obj)
        if user_obj is not None:
            profile_obj = Profile.objects.get(user=user_obj)
            if profile_obj.is_verified == False:
                messages.error(request, 'Not verfied')
                return redirect('login')
            # Authenticate the user
            else:
                print('this line working')
                print('usrname==========',email)
                print('password==========',password)
                user = authenticate(request, username=email, password=password)
                print('user=========', user)
                
                if user is not None:
                    try:
                        cart = Cart.objects.get(cart_id=_cart_id(request))

                        cart_item_exists = CartItem.objects.filter(cart=cart).exists()

                        if cart_item_exists:
                            cart_items = CartItem.objects.filter(cart=cart)
                            product_variations = []
                            for item in cart_items:
                                variatons = item.variation.all()
                                product_variations.append(list(variatons))

                            cart_items = CartItem.objects.filter(user=user)
                            ex_product_variations = []
                            id = []
                            for item in cart_items:
                                ex_variatons = item.variation.all()
                                ex_product_variations.append(list(ex_variatons))
                                id.append(item.id)
                            
                            for prod in product_variations:
                                if prod in ex_product_variations:
                                    index = ex_product_variations.index(prod)
                                    item_id = id[index]
                                    item = CartItem.objects.get(id=item_id)
                                    print('item=====',item)
                                    item.quantity += 1
                                    item.user = user
                                    item.save()

                                else:
                                    cart_items = CartItem.objects.filter(cart=cart)

                                    for cart_item in cart_items:
                                        cart_item.user = user
                                        cart_item.save()
                        # login(request, user)
                        # return redirect('checkout')
                    except:
                        pass
                    # Login the user
                    login(request, user)
                    url = request.META.get('HTTP_REFERER')
                    try:
                        query = requests.utils.urlparse(url).query
                        params = dict(x.split('=') for x in query.split('&'))
                        if 'next' in params:
                            nextPage = params['next']
                            return redirect(nextPage)
                        
                    except:
                        return redirect('home')
                else:
                    messages.error(request, 'Wrong password')
                    return redirect('login')
        
        # If authentication fails or user doesn't exist
        else:
            messages.error(request, 'User is not found')
            return redirect('login')

    return render(request, 'signin.html')




def register(request):

    if request.method == "GET":
        return render(request, 'register.html')
    
    if request.method == "POST":
        username =  request.POST.get('username')
        email =  request.POST.get('email')
        first_name =  request.POST.get('first_name')
        last_name =  request.POST.get('last_name')
        phone_number =  request.POST.get('phone_number')
        password =  request.POST.get('pass1')
        password2 =  request.POST.get('pass2')

        if password != password2:
            messages.error(request, 'The two password fields didn’t match.')
            return redirect('register')
        
        user_obj = Account.objects.filter(username=username).first()
        if user_obj:
            messages.error(request, 'This username is already taken, try another')
            return redirect('register')

        user_obj = Account.objects.filter(email=email).first()
        if user_obj:
            messages.error(request, 'This email is already registerd')
            return redirect('register')


        user_obj = Account.objects.create(first_name=first_name, last_name=last_name,username=username,email=email,phone_number=phone_number)
        user_obj.set_password(password)
        user_obj.save()

        auth_token = str(uuid.uuid4())

        profile = Profile.objects.create(user=user_obj, auth_token=auth_token)
        profile.save()

        send_mail_for_verification(email=email, token=auth_token)
        messages.success(request, 'registered succesfully!, We sent an email for verify your account please check you mail!')

        return redirect('register')

    return render(request, 'register.html')


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')

        profile = Profile.objects.filter(user__email=email).first()
        auth_token = str(uuid.uuid4())
        profile.auth_token = auth_token
        profile.is_verified = False
        profile.save()

        send_mail_for_forgot_password(email, auth_token)
        messages.success(request, 'We send an email for reseting the password')
        return redirect('forgot_password')
    
    return render(request, 'forgot_password.html')


def verify_password(request, auth_token):

    if request.method == "POST":

        password = request.POST.get('password')



        profile = Profile.objects.filter(auth_token=auth_token).first()
        if profile:
            if profile.is_verified:
                messages.error(request, 'You already changed password')
                return redirect('login')

            user = Account.objects.get(profile=profile)
            print('user password', user.password)
            print('input password', password)
            password_match = check_password(password, user.password)
            if password_match:
                messages.error(request, 'Password should not be the same as the old password!')
                return redirect('login')


            user.set_password(password)
            user.save()

            profile.is_verified = True
            profile.save()

            messages.success(request, 'Password changed sucessfully!')
            return redirect('login')
        else:
            messages.error(request, 'Invalid token please try again')
            return redirect('login')

    else:
        return render(request, 'verify_password.html')
    

def send_mail_for_forgot_password(email, auth_token):
    subject = 'Reset the password'
    message = f'Hi Paste the link to reset password http://127.0.0.1:8000/auth/verify_password/{auth_token}'
    from_mail = settings.EMAIL_HOST_USER


    send_mail(
        subject=subject,
        message=message,
        from_email=from_mail,
        recipient_list=[email]
        )

def send_mail_for_verification(email,token):
    subject = 'Your accounts need to verified'
    message = f'Hi Paste the link to verify account http://127.0.0.1:8000/auth/verify/{token} '
    from_mail = settings.EMAIL_HOST_USER


    send_mail(
        subject=subject,
        message=message,
        from_email=from_mail,
        recipient_list=[email]
        )
    
def verify_page(request):
    return render(request, 'verify_page.html')


def verify_user(request,auth_token):

    profile_obj = Profile.objects.filter(auth_token=auth_token).first()
    if profile_obj:
        if profile_obj.is_verified:
            messages.success(request, 'profile already verifed')
            return redirect('login')
        profile_obj.is_verified = True
        profile_obj.save()
        user = Account.objects.filter(profile__auth_token=auth_token).first()
        user.is_active = True
        user.save()
        messages.success(request, 'profile verified successfully')
        return redirect('login')
    







