from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm


# ĐĂNG KÝ TÀI KHOẢN
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            request.session['role'] = user.role
            messages.success(request, 'Đăng ký thành công! Chào mừng bạn đến CourtBooking.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Đăng ký thất bại. Vui lòng kiểm tra lại thông tin.')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


# ĐĂNG NHẬP
def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            request.session['role'] = user.role
            messages.success(request, f'Chào mừng trở lại, {user.username}!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


# ĐĂNG XUẤT
def logout_view(request):
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất.')
    return redirect('accounts:login')


# TRANG CÁ NHÂN
@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')
