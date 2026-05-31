from django import forms

from .models import Court


# FORM ĐĂNG / CHỈNH SÂN (dùng cho owner — không bao gồm owner và is_active)
class CourtForm(forms.ModelForm):

    class Meta:
        model  = Court
        fields = [
            'court_type',
            'name',
            'address',
            'district',
            'description',
            'price_per_hour',
            'image',
        ]
        widgets = {
            'court_type':     forms.Select(attrs={'class': 'form-select'}),
            'name':           forms.TextInput(attrs={'class': 'form-control'}),
            'address':        forms.TextInput(attrs={'class': 'form-control'}),
            'district':       forms.Select(attrs={'class': 'form-select'}),
            'description':    forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price_per_hour': forms.NumberInput(attrs={'class': 'form-control'}),
            'image':          forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
