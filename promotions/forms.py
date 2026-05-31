from django import forms

from .models import Promotion


# FORM QUẢN LÝ MÃ KHUYẾN MẠI
class PromotionForm(forms.ModelForm):

    class Meta:
        model  = Promotion
        fields = '__all__'
        widgets = {
            'code':           forms.TextInput(attrs={'class': 'form-control'}),
            'description':    forms.TextInput(attrs={'class': 'form-control'}),
            'discount_type':  forms.Select(attrs={'class': 'form-select'}),
            'discount_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date':     forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date':       forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active':      forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
