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
            user = form.save(commit=False)

            # LẤY ROLE TỪ FORM (hidden input do tab JS điền)
            role = request.POST.get('role', 'player')

            # BẢO MẬT: chỉ chấp nhận 'player' hoặc 'owner'
            # (chống user F12 sửa thành 'admin')
            if role in ['player', 'owner']:
                user.role = role
            else:
                user.role = 'player'

            user.save()
            login(request, user)
            request.session['role'] = user.role
            messages.success(request, 'Đăng ký thành công! Chào mừng đến CourtBooking.')
            return redirect('courts:court_list')
        else:
            messages.error(request, 'Đăng ký thất bại. Vui lòng kiểm tra lại thông tin.')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


# ĐĂNG NHẬP
def login_view(request):
    if request.user.is_authenticated:
        # ĐẢM BẢO SESSION LUÔN CÓ ROLE (phòng trường hợp login qua /admin/ hoặc session cũ)
        if not request.session.get('role'):
            request.session['role'] = request.user.role
        return redirect('courts:court_list')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # XÁC THỰC ROLE: role chọn ở tab phải khớp role trong DB
            # Admin login không cần check tab (admin login qua bất kỳ tab nào cũng được)
            requested_role = request.POST.get('role')
            if requested_role in ['player', 'owner'] and user.role != 'admin':
                if user.role != requested_role:
                    role_name = 'Chủ sân' if requested_role == 'owner' else 'Người chơi'
                    messages.error(request, f'Tài khoản này không có quyền {role_name}.')
                    return render(request, 'accounts/login.html', {'form': form})

            login(request, user)
            request.session['role'] = user.role  # ĐÚNG CLAUDE.md mục 2.8
            messages.success(request, f'Chào mừng trở lại, {user.username}!')
            return redirect('courts:court_list')
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
