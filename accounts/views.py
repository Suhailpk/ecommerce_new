from django.shortcuts import render, redirect
from .forms import AccountForm
from .models import Account
from django.contrib import messages

# Create your views here.
def register(request):
    if request.method == "POST":
        forms = AccountForm(request.POST)
        if forms.is_valid():
            first_name = forms.cleaned_data['first_name']
            last_name = forms.cleaned_data['last_name']
            email = forms.cleaned_data['email']
            username = email.split('@')[0]
            password = forms.cleaned_data['first_name']
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = forms.cleaned_data['phone_number']
            user.save()
            messages.success(request, 'Registration successfull')
            return redirect('register')
    else:
        forms = AccountForm()
    
    context = {
        'forms': forms
    }
    return render(request, 'register.html', context)


def login(request):
    return render(request, 'signin.html')


