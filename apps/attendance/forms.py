from django import forms
from .models import ManualCheckout
from django.utils import timezone
from datetime import timedelta

class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date,
        label="Start Date"
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date,
        label="End Date"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError("End date cannot be before start date.")
            
            date_range = end_date - start_date
            if date_range > timedelta(days=7):
                raise forms.ValidationError("Date range cannot exceed 7 days.")
        
        return cleaned_data

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