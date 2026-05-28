from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


# FORM ĐĂNG KÝ
class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số điện thoại'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên đăng nhập'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mật khẩu'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nhập lại mật khẩu'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'player'   # mặc định người dùng mới là player
        user.phone = self.cleaned_data.get('phone', '')
        if commit:
            user.save()
        return user


# FORM ĐĂNG NHẬP
class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Tên đăng nhập'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mật khẩu'})
