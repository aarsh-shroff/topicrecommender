from django import forms
from .models import Webpages

class AddressForm(forms.ModelForm):
    class Meta:
        model = Webpages
        fields = "__all__"
        widgets = {'entry': forms.HiddenInput()}