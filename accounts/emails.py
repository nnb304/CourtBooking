from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


# GỬI EMAIL CHỨA LINK KÍCH HOẠT TÀI KHOẢN
# Token của Django tự hết hạn sau PASSWORD_RESET_TIMEOUT và mất hiệu lực khi tài khoản đã kích hoạt
def send_activation_email(request, user):
    uid   = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    link  = request.build_absolute_uri(reverse('accounts:activate', args=[uid, token]))
    context = {'user': user, 'link': link, 'hours': settings.PASSWORD_RESET_TIMEOUT // 3600}
    send_mail(
        subject='[CourtBooking] Xác nhận email đăng ký tài khoản',
        message=render_to_string('accounts/email/activation.txt', context),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=render_to_string('accounts/email/activation.html', context),
    )
