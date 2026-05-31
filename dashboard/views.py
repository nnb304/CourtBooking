from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.shortcuts import redirect, render

from bookings.models import Booking
from courts.models import Court


# TRANG THỐNG KÊ QUẢN TRỊ
@login_required
def dashboard_index(request):
    # KIỂM TRA QUYỀN ADMIN
    if request.session.get('role') != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang quản trị.')
        return redirect('courts:court_list')

    today            = date.today()
    start_of_week    = today - timedelta(days=today.weekday())   # Thứ Hai đầu tuần
    first_of_month   = today.replace(day=1)

    # DOANH THU (chỉ tính booking đã xác nhận, lọc theo ngày tạo đơn)
    revenue_today = (
        Booking.objects
        .filter(status='confirmed', created_at__date=today)
        .aggregate(total=Sum('total_price'))['total'] or 0
    )
    revenue_month = (
        Booking.objects
        .filter(
            status='confirmed',
            created_at__year=today.year,
            created_at__month=today.month,
        )
        .aggregate(total=Sum('total_price'))['total'] or 0
    )

    # SỐ LƯỢNG ĐƠN ĐẶT SÂN (đã xác nhận)
    count_today = Booking.objects.filter(
        status='confirmed', created_at__date=today
    ).count()
    count_week  = Booking.objects.filter(
        status='confirmed', created_at__date__gte=start_of_week
    ).count()
    count_month = Booking.objects.filter(
        status='confirmed',
        created_at__year=today.year,
        created_at__month=today.month,
    ).count()

    # TOP 3 SÂN ĐƯỢC ĐẶT NHIỀU NHẤT
    top_courts = (
        Court.objects
        .annotate(num_bookings=Count(
            'bookings',
            filter=Q(bookings__status='confirmed'),
        ))
        .order_by('-num_bookings')[:3]
    )

    # 10 BOOKING GẦN NHẤT
    recent_bookings = (
        Booking.objects
        .select_related('court', 'user')
        .order_by('-created_at')[:10]
    )

    # DỮ LIỆU BIỂU ĐỒ: DOANH THU 7 NGÀY GẦN NHẤT (T-6 → hôm nay)
    chart_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        rev = (
            Booking.objects
            .filter(status='confirmed', created_at__date=day)
            .aggregate(total=Sum('total_price'))['total'] or 0
        )
        chart_data.append({
            'date':    day.strftime('%d/%m'),
            'revenue': int(rev),
        })

    return render(request, 'dashboard/index.html', {
        'revenue_today':   revenue_today,
        'revenue_month':   revenue_month,
        'count_today':     count_today,
        'count_week':      count_week,
        'count_month':     count_month,
        'top_courts':      top_courts,
        'recent_bookings': recent_bookings,
        'chart_data':      chart_data,
    })
