from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from .models import Court, Favorite
from reviews.forms import ReviewForm


def _get_favorited_ids(user):
    """Trả về list id sân user đã thích, hoặc [] nếu chưa đăng nhập."""
    if user.is_authenticated:
        return list(Favorite.objects.filter(user=user).values_list('court_id', flat=True))
    return []


# TRANG CHỦ - DANH SÁCH SÂN NỔI BẬT (có tìm kiếm và lọc)
def home_view(request):
    courts = Court.objects.filter(is_active=True).annotate(
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
        courts = courts.filter(name__icontains=q)
    if court_type:
        courts = courts.filter(court_type=court_type)
    if district:
        courts = courts.filter(district=district)
    if price_max:
        courts = courts.filter(price_per_hour__lte=price_max)

    context = {
        'courts':       courts,
        'q':            q,
        'court_type':   court_type,
        'district':     district,
        'price_max':    price_max,
        'court_type_choices': Court.COURT_TYPE_CHOICES,
        'district_choices':   Court.DISTRICT_CHOICES,
        'favorited_ids':      _get_favorited_ids(request.user),
    }
    return render(request, 'courts/home.html', context)


# CHI TIẾT SÂN
def court_detail_view(request, pk):
    court = get_object_or_404(Court, pk=pk)

    # LẤY DANH SÁCH VÀ THỐNG KÊ ĐÁNH GIÁ
    reviews_list  = court.reviews.select_related('user').all()
    review_count  = reviews_list.count()
    avg_data      = court.reviews.aggregate(a=Avg('rating'))
    avg_rating    = avg_data['a']                            # None nếu chưa có đánh giá
    avg_rounded   = round(avg_rating) if avg_rating else 0  # làm tròn để vẽ sao

    # KIỂM TRA USER ĐÃ ĐÁNH GIÁ CHƯA
    has_reviewed = False
    if request.user.is_authenticated:
        has_reviewed = court.reviews.filter(user=request.user).exists()

    context = {
        'court':         court,
        'favorited_ids': _get_favorited_ids(request.user),
        'reviews_list':  reviews_list,
        'review_count':  review_count,
        'avg_rating':    avg_rating,
        'avg_rounded':   avg_rounded,
        'has_reviewed':  has_reviewed,
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
            fav.delete()   # đã thích -> bỏ thích
        else:
            Favorite.objects.create(user=request.user, court=court)
    # quay lại trang trước, hoặc về trang chủ nếu không có referer
    referer = request.META.get('HTTP_REFERER', '')
    return redirect(referer if referer else 'courts:home')


# DANH SÁCH SÂN YÊU THÍCH CỦA USER
@login_required
def favorite_list_view(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('court')
    courts = [fav.court for fav in favorites]
    # tất cả sân trong trang này đều đã thích
    favorited_ids = [c.id for c in courts]
    context = {
        'courts':        courts,
        'favorited_ids': favorited_ids,
    }
    return render(request, 'courts/favorite_list.html', context)
