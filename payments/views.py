import random
from datetime import datetime
from urllib.parse import quote

from django.conf import settings

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from bookings.models import Booking

from .forms import PaymentForm
from .models import Payment


# XỬ LÝ THANH TOÁN
@login_required
def payment_process(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)

    # CHỈ CHỦ BOOKING MỚI ĐƯỢC VÀO
    if booking.user != request.user:
        messages.error(request, 'Bạn không có quyền truy cập đơn đặt sân này.')
        return redirect('bookings:booking_list')

    # ĐƠN CHỜ QUÁ HẠN GIỮ CHỖ → TỰ HUỶ, NHẢ KHUNG GIỜ
    if booking.is_hold_expired:
        booking.cancel()
        messages.error(request, 'Đơn đã quá hạn thanh toán nên bị huỷ. Vui lòng đặt lại.')
        return redirect('bookings:booking_list')

    # ĐƠN ĐÃ HUỶ THÌ KHÔNG THANH TOÁN ĐƯỢC
    if booking.status == 'cancelled':
        messages.error(request, 'Đơn đặt sân này đã bị huỷ.')
        return redirect('bookings:booking_list')

    # NẾU ĐÃ THANH TOÁN THÀNH CÔNG THÌ KHÔNG CHO VÀO LẠI
    existing = Payment.objects.filter(booking=booking).first()
    if existing and existing.status == 'success':
        messages.info(request, 'Đơn đặt sân này đã được thanh toán thành công.')
        return redirect('bookings:booking_list')

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # TẠO HOẶC CẬP NHẬT BẢN GHI PAYMENT
                payment, _ = Payment.objects.get_or_create(booking=booking)
                payment.method = form.cleaned_data['method']

                # GIẢ LẬP KẾT QUẢ: chuyển khoản QR coi như thành công khi khách bấm xác nhận,
                # các phương thức khác 90% thành công
                if payment.method == 'banking' or random.random() < 0.9:
                    payment.status  = 'success'
                    payment.paid_at = datetime.now()
                    payment.save()

                    booking.status = 'confirmed'
                    booking.save()

                    messages.success(
                        request,
                        f'Thanh toán thành công! Đơn đặt sân "{booking.court.name}" đã được xác nhận.'
                    )
                else:
                    payment.status = 'failed'
                    payment.save()
                    messages.error(
                        request,
                        'Thanh toán thất bại. Vui lòng thử lại hoặc chọn phương thức khác.'
                    )
                    # THẤT BẠI: ở lại trang thanh toán để thử lại trong thời gian giữ chỗ
                    return redirect('payments:payment_process', booking_id=booking.pk)

            return redirect('bookings:booking_list')

    else:
        form = PaymentForm()

    return render(request, 'payments/payment_process.html', {
        'booking':     booking,
        'form':        form,
        'qr':          build_vietqr(booking),
    })


def build_vietqr(booking):
    """Tạo link ảnh VietQR (img.vietqr.io) có sẵn số tiền + nội dung chuyển khoản theo mã đơn."""
    transfer_note = f'CB{booking.pk}'
    if not (settings.VIETQR_BANK_ID and settings.VIETQR_ACCOUNT_NO):
        return {'configured': False, 'note': transfer_note}
    url = (
        f'https://img.vietqr.io/image/{settings.VIETQR_BANK_ID}-{settings.VIETQR_ACCOUNT_NO}-compact2.png'
        f'?amount={int(booking.total_price)}'
        f'&addInfo={quote(transfer_note)}'
        f'&accountName={quote(settings.VIETQR_ACCOUNT_NAME)}'
    )
    return {
        'configured':   True,
        'url':          url,
        'note':         transfer_note,
        'bank':         settings.VIETQR_BANK_ID,
        'account_no':   settings.VIETQR_ACCOUNT_NO,
        'account_name': settings.VIETQR_ACCOUNT_NAME,
    }
