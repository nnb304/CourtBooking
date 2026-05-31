import random
from datetime import datetime

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

                # GIẢ LẬP KẾT QUẢ: 90% THÀNH CÔNG
                if random.random() < 0.9:
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

            return redirect('bookings:booking_list')

    else:
        form = PaymentForm()

    return render(request, 'payments/payment_process.html', {
        'booking': booking,
        'form':    form,
    })
