from django import forms

from .models import Court


# FORM QUẢN LÝ SÂN
class CourtForm(forms.ModelForm):

    class Meta:
        model  = Court
        fields = '__all__'
        widgets = {
            'name':           forms.TextInput(attrs={'class': 'form-control'}),
            'court_type':     forms.Select(attrs={'class': 'form-select'}),
            'address':        forms.TextInput(attrs={'class': 'form-control'}),
            'district':       forms.Select(attrs={'class': 'form-select'}),
            'description':    forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price_per_hour': forms.NumberInput(attrs={'class': 'form-control'}),
            'image':          forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active':      forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'owner':          forms.Select(attrs={'class': 'form-select'}),
        }
