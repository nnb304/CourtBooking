from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PromotionForm
from .models import Promotion


def _fmt(n):
    """Format số theo kiểu Việt Nam: dấu chấm hàng nghìn."""
    return f"{int(n):,}".replace(',', '.')


# DANH SÁCH MÃ KHUYẾN MẠI (chỉ admin)
def promotion_list(request):
    if request.session.get('role') != 'admin':
        return redirect('accounts:login')

    promos_qs   = Promotion.objects.all().order_by('-created_at')
    paginator   = Paginator(promos_qs, 15)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)
    return render(request, 'promotions/promotion_list.html', {'page_obj': page_obj})


# THÊM MÃ KHUYẾN MẠI (chỉ admin)
def promotion_create(request):
    if request.session.get('role') != 'admin':
        return redirect('accounts:login')

    if request.method == 'POST':
        form = PromotionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã tạo mã khuyến mãi mới.')
            return redirect('promotions:promotion_list')
    else:
        form = PromotionForm()

    return render(request, 'promotions/promotion_form.html', {
        'form':        form,
        'action_text': 'Tạo mã khuyến mãi',
    })


# SỬA MÃ KHUYẾN MẠI (chỉ admin)
def promotion_update(request, pk):
    if request.session.get('role') != 'admin':
        return redirect('accounts:login')

    promo = get_object_or_404(Promotion, pk=pk)

    if request.method == 'POST':
        form = PromotionForm(request.POST, instance=promo)
        if form.is_valid():
            form.save()
            messages.success(request, f'Đã cập nhật mã "{promo.code}".')
            return redirect('promotions:promotion_list')
    else:
        form = PromotionForm(instance=promo)

    return render(request, 'promotions/promotion_form.html', {
        'form':        form,
        'action_text': f'Sửa mã — {promo.code}',
        'promo':       promo,
    })


# XÓA MÃ KHUYẾN MẠI (chỉ admin)
def promotion_delete(request, pk):
    if request.session.get('role') != 'admin':
        return redirect('accounts:login')

    promo = get_object_or_404(Promotion, pk=pk)

    if request.method == 'POST':
        code = promo.code
        promo.delete()
        messages.success(request, f'Đã xóa mã "{code}".')
        return redirect('promotions:promotion_list')

    return render(request, 'promotions/promotion_confirm_delete.html', {'promo': promo})


# VALIDATE MÃ KHUYẾN MẠI — NHẬN POST, TRẢ JSON
@login_required
@require_POST
def validate_promo(request):
    code        = request.POST.get('code', '').strip()
    order_total = request.POST.get('order_total', '0')

    try:
        order_total = int(order_total)
    except (ValueError, TypeError):
        order_total = 0

    # TÌM MÃ (không phân biệt hoa/thường)
    try:
        promo = Promotion.objects.get(code__iexact=code)
    except Promotion.DoesNotExist:
        return JsonResponse({'valid': False, 'message': f'Mã "{code}" không tồn tại.'})

    # KIỂM TRA CÒN HIỆU LỰC
    if not promo.is_valid_now():
        return JsonResponse({
            'valid':   False,
            'message': f'Mã "{promo.code}" đã hết hạn hoặc không còn hiệu lực.',
        })

    # TÍNH SỐ TIỀN GIẢM
    if promo.discount_type == 'percent':
        discount_amount = int(order_total * promo.discount_value / 100)
    else:
        discount_amount = min(int(promo.discount_value), order_total)

    final_price = order_total - discount_amount
    message     = f'Áp dụng mã {promo.code} — giảm {_fmt(discount_amount)}đ'

    return JsonResponse({
        'valid':           True,
        'promo_id':        promo.pk,
        'discount_amount': discount_amount,
        'final_price':     final_price,
        'message':         message,
    })
