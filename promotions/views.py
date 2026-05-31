from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Promotion


def _fmt(n):
    """Format số theo kiểu Việt Nam: dấu chấm hàng nghìn."""
    return f"{int(n):,}".replace(',', '.')


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
        # flat: không được vượt quá tổng tiền gốc
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
