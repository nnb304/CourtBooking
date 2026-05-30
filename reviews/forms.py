from django import forms
from .models import Review


# FORM GỬI ĐÁNH GIÁ SÂN
class ReviewForm(forms.ModelForm):

    class Meta:
        model  = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={
                'class':       'form-control',
                'rows':        3,
                'placeholder': 'Chia sẻ trải nghiệm của bạn về sân...',
                'maxlength':   500,
            }),
        }
        labels = {
            'rating':  'Đánh giá',
            'comment': 'Nhận xét',
        }
