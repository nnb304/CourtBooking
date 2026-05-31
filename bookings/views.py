from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from courts.models import Court
from promotions.models import Promotion

from .forms import BookingForm
from .models import Booking


def _time_to_slot(t):
    """Chuyển time → slot index. Slot 0 = 06:00, mỗi slot 30 phút. Clamp về [0, 32]."""
    idx = (t.hour - 6) * 2 + (1 if t.minute >= 30 else 0)
    return max(0, min(32, idx))


# TẠO ĐƠN ĐẶT SÂN (hiển thị lưới time-slot)
@login_required
def booking_create(request, court_id):
    court = get_object_or_404(Court, pk=court_id, is_active=True)
    today = date.today()

    if request.method == 'POST':
        form = BookingForm(request.POST, court=court)
        # ĐỌC NGÀY TỪ POST (hidden field trong form)
        date_str = request.POST.get('date', '')
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            selected_date = today

        if form.is_valid():
            booking       = form.save(commit=False)
            booking.user  = request.user
            booking.court = court

            # TÍNH TỔNG TIỀN GỐC = giá/giờ × số giờ thuê
            order_total         = court.price_per_hour * form.cleaned_data['duration_hours']
            booking.total_price = order_total

            # ÁP MÃ KHUYẾN MẠI NẾU CÓ (server tự tính lại, không tin client)
            promo_code_str = request.POST.get('promotion', '').strip()
            if promo_code_str:
                try:
                    promo = Promotion.objects.get(code__iexact=promo_code_str)
                    if promo.is_valid_now():
                        if promo.discount_type == 'percent':
                            discount = int(order_total * promo.discount_value / 100)
                        else:
                            discount = min(int(promo.discount_value), int(order_total))
                        booking.promotion       = promo
                        booking.discount_amount = discount
                        booking.total_price     = order_total - discount
                except Promotion.DoesNotExist:
                    pass  # mã không tồn tại hoặc đã bị xóa → bỏ qua

            booking.save()
            messages.success(request, f'Đặt sân "{court.name}" thành công! Vui lòng thanh toán để xác nhận.')
            return redirect('payments:payment_process', booking_id=booking.pk)

    else:
        form = BookingForm(court=court)
        # ĐỌC NGÀY TỪ GET (khi user chọn ngày trên lưới)
        date_str = request.GET.get('date', '')
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            selected_date = today
        # Không cho xem lịch ngày quá khứ
        if selected_date < today:
            selected_date = today

    # LẤY BOOKING ĐÃ ĐẶT CỦA SÂN TRONG NGÀY ĐƯỢC CHỌN
    existing_bookings = Booking.objects.filter(
        court=court,
        date=selected_date,
    ).exclude(status='cancelled')

    # XÂY DỰNG TẬP SLOT ĐÃ BỊ CHIẾM
    booked_slots = set()
    for b in existing_bookings:
        start_idx = _time_to_slot(b.start_time)
        end_idx   = start_idx + b.duration_hours * 2   # 1 giờ = 2 slot
        for i in range(start_idx, min(end_idx, 32)):
            booked_slots.add(i)

    # SLOT GIỜ ĐÃ QUA (chỉ áp dụng khi xem lịch ngày hôm nay)
    past_slots = set()
    if selected_date == today:
        current_slot = _time_to_slot(datetime.now().time())
        past_slots   = set(range(0, current_slot + 1))

    # TẠO DANH SÁCH 32 SLOT (06:00 → 21:30)
    slots_info = []
    for idx in range(32):
        hour   = 6 + idx // 2
        minute = 30 if idx % 2 == 1 else 0
        slots_info.append({
            'index':      idx,
            'time_label': f'{hour:02d}:{minute:02d}',
            'is_booked':  idx in booked_slots,
            'is_past':    idx in past_slots,
        })

    context = {
        'form':              form,
        'court':             court,
        'selected_date':     selected_date,
        'selected_date_str': selected_date.strftime('%Y-%m-%d'),
        'today_str':         today.strftime('%Y-%m-%d'),
        'slots_info':        slots_info,
    }
    return render(request, 'bookings/booking_form.html', context)


# DANH SÁCH ĐƠN ĐẶT SÂN CỦA TÔI
@login_required
def booking_list(request):
    bookings_qs = Booking.objects.filter(user=request.user).select_related('court', 'promotion')
    paginator   = Paginator(bookings_qs, 10)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)
    return render(request, 'bookings/my_bookings.html', {'page_obj': page_obj})
