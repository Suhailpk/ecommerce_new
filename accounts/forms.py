from django import forms
from .models import Account


class AccountForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter the password'}))
    
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Confirm the password'}))
    

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number']
    
    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter you first name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter you last name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter you email address'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter you phone number'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(AccountForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError('Password not match!')