
from django import forms
from .models import ManualCheckout
from django.utils import timezone

class ManualCheckoutForm(forms.ModelForm):
    checkout_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        initial=timezone.now,
        label="Checkout Time"
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,
        label="Reason for Manual Checkout"
    )
    
    class Meta:
        model = ManualCheckout
        fields = ['checkout_time', 'reason']