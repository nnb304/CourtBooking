from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from .emails import send_activation_email
from .forms import RegisterForm, LoginForm
from .models import User


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

            # CHƯA KÍCH HOẠT CHO ĐẾN KHI BẤM LINK TRONG EMAIL
            user.is_active = False
            user.save()
            send_activation_email(request, user)
            messages.success(
                request,
                f'Đăng ký thành công! Vui lòng mở email {user.email} và bấm link xác nhận để kích hoạt tài khoản.'
            )
            return redirect('accounts:login')
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
            # TÀI KHOẢN CHƯA XÁC NHẬN EMAIL: đúng mật khẩu thì gửi lại link kích hoạt
            pending = User.objects.filter(username=request.POST.get('username', ''), is_active=False).first()
            if pending and pending.check_password(request.POST.get('password', '')):
                send_activation_email(request, pending)
                form = LoginForm()
                messages.warning(
                    request,
                    f'Tài khoản chưa xác nhận email. Đã gửi lại link kích hoạt tới {pending.email}.'
                )
            else:
                messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


# KÍCH HOẠT TÀI KHOẢN TỪ LINK TRONG EMAIL
def activate_view(request, uidb64, token):
    try:
        user = User.objects.get(pk=force_str(urlsafe_base64_decode(uidb64)))
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user is not None and user.is_active:
        messages.info(request, 'Tài khoản đã được kích hoạt trước đó, bạn có thể đăng nhập.')
    elif user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=['is_active'])
        messages.success(request, 'Xác nhận email thành công! Bạn có thể đăng nhập.')
    else:
        messages.error(request, 'Link kích hoạt không hợp lệ hoặc đã hết hạn. Đăng nhập lại để nhận link mới.')
    return redirect('accounts:login')


# ĐĂNG XUẤT
def logout_view(request):
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất.')
    return redirect('accounts:login')


# TRANG CÁ NHÂN
@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')
