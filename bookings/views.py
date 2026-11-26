from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render

from courts.models import Court
from promotions.models import Promotion

from .forms import BookingForm
from .models import (
    CLOSE_HOUR, HOLD_MINUTES, OPEN_HOUR, SLOT_MINUTES, TOTAL_SLOTS,
    Booking, BookingSlot, expire_stale_pending, time_to_slot,
)


def _parse_date(value, default):
    try:
        return datetime.strptime(value or '', '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return default


def calculate_discount(promo, order_total):
    """Tính số tiền giảm của 1 mã trên tổng tiền gốc (server tự tính, không tin client)."""
    if promo.discount_type == 'percent':
        return int(order_total * promo.discount_value / 100)
    return min(int(promo.discount_value), int(order_total))


# TẠO ĐƠN ĐẶT SÂN (hiển thị lưới time-slot)
@login_required
def booking_create(request, court_id):
    court = get_object_or_404(Court, pk=court_id, is_active=True)
    today = date.today()

    # NHẢ CÁC KHUNG GIỜ CỦA ĐƠN CHỜ THANH TOÁN ĐÃ QUÁ HẠN
    expire_stale_pending(court=court)

    if request.method == 'POST':
        form = BookingForm(request.POST, court=court)
        selected_date = _parse_date(request.POST.get('date'), today)

        if form.is_valid():
            booking       = form.save(commit=False)
            booking.user  = request.user
            booking.court = court

            # GIÁ GỐC = giá/giờ × số giờ thuê (lưu cố định để đối chiếu thuế)
            order_total            = court.price_per_hour * form.cleaned_data['duration_hours']
            booking.original_price = order_total
            booking.total_price    = order_total

            # ÁP MÃ KHUYẾN MẠI NẾU CÓ
            promo_code_str = request.POST.get('promotion', '').strip()
            if promo_code_str:
                promo = Promotion.objects.filter(code__iexact=promo_code_str).first()
                if promo and promo.is_valid_now():
                    discount                = calculate_discount(promo, order_total)
                    booking.promotion       = promo
                    booking.discount_amount = discount
                    booking.total_price     = order_total - discount
                else:
                    messages.warning(request, 'Mã khuyến mãi không hợp lệ hoặc đã hết hạn, đơn được tính giá gốc.')

            # LỚP 2: LƯU ĐƠN + GIỮ TỪNG SLOT TRONG 1 TRANSACTION.
            # Nếu 2 người đặt chồng giờ cùng lúc, UNIQUE(court, date, slot) ở DB sẽ chặn người sau.
            try:
                with transaction.atomic():
                    booking.save()
                    booking.reserve_slots()
            except IntegrityError:
                messages.error(
                    request,
                    'Khung giờ vừa được người khác đặt, vui lòng chọn khung giờ khác.'
                )
                return redirect(f"{request.path}?date={selected_date:%Y-%m-%d}")

            messages.success(
                request,
                f'Đã giữ chỗ sân "{court.name}". Vui lòng thanh toán trong {HOLD_MINUTES} phút để xác nhận.'
            )
            return redirect('payments:payment_process', booking_id=booking.pk)

    else:
        form = BookingForm(court=court)
        selected_date = _parse_date(request.GET.get('date'), today)
        if selected_date < today:   # Không cho xem lịch ngày quá khứ
            selected_date = today

    # SLOT ĐÃ BỊ CHIẾM (đọc thẳng từ bảng BookingSlot)
    booked_slots = set(
        BookingSlot.objects.filter(court=court, date=selected_date).values_list('slot', flat=True)
    )

    # SLOT GIỜ ĐÃ QUA (chỉ áp dụng khi xem lịch ngày hôm nay)
    past_slots = set()
    if selected_date == today:
        now = datetime.now().time()
        if now.hour >= OPEN_HOUR:
            past_slots = set(range(0, min(time_to_slot(now) + 1, TOTAL_SLOTS)))

    # TẠO DANH SÁCH SLOT (06:00 → 21:30)
    slots_info = []
    for idx in range(TOTAL_SLOTS):
        minutes = OPEN_HOUR * 60 + idx * SLOT_MINUTES
        slots_info.append({
            'index':      idx,
            'time_label': f'{minutes // 60:02d}:{minutes % 60:02d}',
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
        'close_hour':        CLOSE_HOUR,
    }
    return render(request, 'bookings/booking_form.html', context)


# DANH SÁCH BOOKING CÁC SÂN CỦA OWNER (read-only)
@login_required
def owner_booking_list(request):
    # KIỂM TRA QUYỀN THEO TÀI KHOẢN TRONG DB (không dựa vào session)
    if request.user.role != 'owner':
        messages.error(request, 'Chỉ chủ sân mới xem được trang này.')
        return redirect('courts:court_list')

    expire_stale_pending()

    current_status = request.GET.get('status', '').strip()
    bookings_qs = (
        Booking.objects
        .filter(court__owner=request.user)
        .select_related('court', 'user', 'promotion', 'payment')
        .order_by('-date', '-created_at')
    )
    if current_status in ('pending', 'confirmed', 'cancelled'):
        bookings_qs = bookings_qs.filter(status=current_status)
    else:
        current_status = ''   # chuẩn hoá để template dễ so sánh

    # TỔNG ĐỐI CHIẾU: giá gốc / giảm giá / thực thu theo bộ lọc hiện tại
    totals = bookings_qs.aggregate(
        count=Count('id'),
        original=Sum('original_price'),
        discount=Sum('discount_amount'),
        actual=Sum('total_price'),
    )

    paginator = Paginator(bookings_qs, 10)
    page_obj  = paginator.get_page(request.GET.get('page'))

    return render(request, 'bookings/owner_booking_list.html', {
        'page_obj':       page_obj,
        'current_status': current_status,
        'totals':         totals,
    })


# DANH SÁCH ĐƠN ĐẶT SÂN CỦA TÔI
@login_required
def booking_list(request):
    expire_stale_pending()
    bookings_qs = Booking.objects.filter(user=request.user).select_related('court', 'promotion')
    paginator   = Paginator(bookings_qs, 10)
    page_obj    = paginator.get_page(request.GET.get('page'))
    return render(request, 'bookings/my_bookings.html', {'page_obj': page_obj})
