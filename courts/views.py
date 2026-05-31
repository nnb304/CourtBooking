from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render

from bookings.models import Booking
from reviews.forms import ReviewForm

from .forms import CourtForm
from .models import Court, Favorite


def _get_favorited_ids(user):
    """Trả về list id sân user đã thích, hoặc [] nếu chưa đăng nhập."""
    if user.is_authenticated:
        return list(Favorite.objects.filter(user=user).values_list('court_id', flat=True))
    return []


# TRANG CHỦ - DANH SÁCH SÂN (có tìm kiếm, lọc và phân trang)
def court_list(request):
    courts_qs = Court.objects.filter(is_active=True).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews'),
    )

    # ĐỌC THAM SỐ TÌM KIẾM / LỌC TỪ GET
    q          = request.GET.get('q', '').strip()
    court_type = request.GET.get('court_type', '')
    district   = request.GET.get('district', '')
    price_max  = request.GET.get('price_max', '')

    # ÁP FILTER THEO TỪNG THAM SỐ NẾU CÓ GIÁ TRỊ
    if q:
        courts_qs = courts_qs.filter(name__icontains=q)
    if court_type:
        courts_qs = courts_qs.filter(court_type=court_type)
    if district:
        courts_qs = courts_qs.filter(district=district)
    if price_max:
        courts_qs = courts_qs.filter(price_per_hour__lte=price_max)

    # PHÂN TRANG
    paginator   = Paginator(courts_qs, 10)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)

    context = {
        'page_obj':           page_obj,
        'q':                  q,
        'court_type':         court_type,
        'district':           district,
        'price_max':          price_max,
        'court_type_choices': Court.COURT_TYPE_CHOICES,
        'district_choices':   Court.DISTRICT_CHOICES,
        'favorited_ids':      _get_favorited_ids(request.user),
    }
    return render(request, 'courts/home.html', context)


# CHI TIẾT SÂN
def court_detail(request, pk):
    court = get_object_or_404(Court, pk=pk)

    # LẤY DANH SÁCH VÀ THỐNG KÊ ĐÁNH GIÁ
    reviews_list = court.reviews.select_related('user').all()
    review_count = reviews_list.count()
    avg_data     = court.reviews.aggregate(a=Avg('rating'))
    avg_rating   = avg_data['a']
    avg_rounded  = round(avg_rating) if avg_rating else 0

    # KIỂM TRA USER ĐÃ ĐÁNH GIÁ CHƯA VÀ CÓ QUYỀN ĐÁNH GIÁ KHÔNG
    has_reviewed = False
    can_review   = False
    if request.user.is_authenticated:
        has_reviewed = court.reviews.filter(user=request.user).exists()
        can_review   = Booking.objects.filter(
            user=request.user, court=court, status='confirmed',
        ).exists()

    context = {
        'court':         court,
        'favorited_ids': _get_favorited_ids(request.user),
        'reviews_list':  reviews_list,
        'review_count':  review_count,
        'avg_rating':    avg_rating,
        'avg_rounded':   avg_rounded,
        'has_reviewed':  has_reviewed,
        'can_review':    can_review,
        'review_form':   ReviewForm(),
    }
    return render(request, 'courts/court_detail.html', context)


# THÊM / BỎ SÂN YÊU THÍCH (toggle)
@login_required
def toggle_favorite_view(request, pk):
    if request.method == 'POST':
        court = get_object_or_404(Court, pk=pk)
        fav = Favorite.objects.filter(user=request.user, court=court)
        if fav.exists():
            fav.delete()   # đã thích → bỏ thích
        else:
            Favorite.objects.create(user=request.user, court=court)
    # quay lại trang trước, hoặc về trang chủ nếu không có referer
    referer = request.META.get('HTTP_REFERER', '')
    return redirect(referer if referer else 'courts:court_list')


# DANH SÁCH SÂN CỦA OWNER (chỉ owner mới vào được)
def my_court_list(request):
    if request.session.get('role') != 'owner':
        return redirect('accounts:login')

    courts_qs   = Court.objects.filter(owner=request.user).order_by('-id')
    paginator   = Paginator(courts_qs, 10)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)
    return render(request, 'courts/my_court_list.html', {'page_obj': page_obj})


# THÊM SÂN MỚI (chỉ owner)
def court_create(request):
    if request.session.get('role') != 'owner':
        return redirect('accounts:login')

    if request.method == 'POST':
        form = CourtForm(request.POST, request.FILES)
        if form.is_valid():
            court           = form.save(commit=False)
            court.owner     = request.user   # gán chủ sân
            court.is_active = False          # chờ admin duyệt
            court.save()
            messages.success(request, 'Đã gửi sân chờ admin duyệt!')
            return redirect('courts:my_court_list')
    else:
        form = CourtForm()

    return render(request, 'courts/court_form.html', {
        'form':        form,
        'action_text': 'Đăng sân mới',
    })


# CẬP NHẬT SÂN (chỉ owner — chỉ sân của mình)
def court_update(request, pk):
    if request.session.get('role') != 'owner':
        return redirect('accounts:login')

    court = get_object_or_404(Court, pk=pk)

    # KIỂM TRA QUYỀN SỞ HỮU
    if court.owner != request.user:
        messages.error(request, 'Bạn không có quyền sửa sân này.')
        return redirect('courts:my_court_list')

    if request.method == 'POST':
        form = CourtForm(request.POST, request.FILES, instance=court)
        if form.is_valid():
            form.save()
            messages.success(request, f'Đã cập nhật sân "{court.name}".')
            return redirect('courts:my_court_list')
    else:
        form = CourtForm(instance=court)

    return render(request, 'courts/court_form.html', {
        'form':        form,
        'action_text': 'Cập nhật sân',
        'court':       court,
    })


# XÓA SÂN (chỉ owner — chỉ sân của mình)
def court_delete(request, pk):
    if request.session.get('role') != 'owner':
        return redirect('accounts:login')

    court = get_object_or_404(Court, pk=pk)

    # KIỂM TRA QUYỀN SỞ HỮU
    if court.owner != request.user:
        messages.error(request, 'Bạn không có quyền xóa sân này.')
        return redirect('courts:my_court_list')

    if request.method == 'POST':
        name = court.name
        court.delete()
        messages.success(request, f'Đã xóa sân "{name}".')
        return redirect('courts:my_court_list')

    return render(request, 'courts/court_confirm_delete.html', {'court': court})


# DANH SÁCH SÂN CHỜ DUYỆT (chỉ admin)
def court_pending_list(request):
    if request.session.get('role') != 'admin':
        return redirect('accounts:login')

    pending_qs  = Court.objects.filter(is_active=False).order_by('-id')
    paginator   = Paginator(pending_qs, 10)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)
    return render(request, 'courts/court_pending_list.html', {'page_obj': page_obj})


# DUYỆT SÂN — CHỈ CHẤP NHẬN POST (chỉ admin)
def court_approve(request, pk):
    if request.session.get('role') != 'admin':
        return redirect('accounts:login')

    # GET KHÔNG CHO THAO TÁC — redirect về danh sách
    if request.method != 'POST':
        return redirect('courts:court_pending_list')

    court           = get_object_or_404(Court, pk=pk)
    court.is_active = True
    court.save()
    messages.success(request, f'Đã duyệt sân "{court.name}".')
    return redirect('courts:court_pending_list')


# TỪ CHỐI SÂN (GET xác nhận, POST xóa — chỉ admin)
def court_reject(request, pk):
    if request.session.get('role') != 'admin':
        return redirect('accounts:login')

    court = get_object_or_404(Court, pk=pk)

    if request.method == 'POST':
        name = court.name
        court.delete()
        messages.success(request, f'Đã từ chối và xóa sân "{name}".')
        return redirect('courts:court_pending_list')

    return render(request, 'courts/court_reject_confirm.html', {'court': court})


# DANH SÁCH SÂN YÊU THÍCH CỦA USER
@login_required
def favorite_list_view(request):
    favorites    = Favorite.objects.filter(user=request.user).select_related('court')
    courts       = [fav.court for fav in favorites]
    # tất cả sân trong trang này đều đã thích
    favorited_ids = [c.id for c in courts]
    context = {
        'courts':        courts,
        'favorited_ids': favorited_ids,
    }
    return render(request, 'courts/favorite_list.html', context)
