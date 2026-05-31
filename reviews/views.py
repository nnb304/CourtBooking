from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from courts.models import Court
from .models import Review
from .forms import ReviewForm


# GỬI ĐÁNH GIÁ SÂN
@login_required
def review_create(request, court_id):
    court = get_object_or_404(Court, pk=court_id)

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
