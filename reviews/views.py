from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from bookings.models import Booking
from courts.models import Court

from .forms import ReviewForm
from .models import Review


# GỬI ĐÁNH GIÁ SÂN
def review_create(request, court_id):
    court = get_object_or_404(Court, pk=court_id)

    # KIỂM TRA ĐĂNG NHẬP THỦ CÔNG
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    # KIỂM TRA QUYỀN ĐÁNH GIÁ: phải có booking confirmed cho sân này
    has_confirmed_booking = Booking.objects.filter(
        user=request.user,
        court=court,
        status='confirmed',
    ).exists()

    if not has_confirmed_booking:
        messages.error(
            request,
            'Bạn chỉ được đánh giá sân đã đặt và thanh toán thành công.',
        )
        return redirect('courts:court_detail', pk=court.pk)

    # CHỈ NHẬN POST
    if request.method != 'POST':
        return redirect('courts:court_detail', pk=court.pk)

    # KIỂM TRA ĐÃ REVIEW CHƯA
    if Review.objects.filter(court=court, user=request.user).exists():
        messages.warning(request, 'Bạn đã đánh giá sân này rồi.')
        return redirect('courts:court_detail', pk=court.pk)

    form = ReviewForm(request.POST)
    if form.is_valid():
        review       = form.save(commit=False)
        review.court = court
        review.user  = request.user
        review.save()
        messages.success(request, 'Cảm ơn bạn đã đánh giá!')
    else:
        messages.error(request, 'Đánh giá không hợp lệ. Vui lòng kiểm tra lại.')

    return redirect('courts:court_detail', pk=court.pk)
