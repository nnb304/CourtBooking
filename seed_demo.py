from datetime import date, datetime, timedelta, time
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from courts.models import Court, Favorite
from bookings.models import Booking
from promotions.models import Promotion

User = get_user_model()

# Helper: tao datetime aware/naive tuy USE_TZ
def make_dt(y, m, d, h=0, mi=0):
    dt = datetime(y, m, d, h, mi)
    if settings.USE_TZ:
        dt = timezone.make_aware(dt)
    return dt

print("\n" + "="*60)
print("SEED DATA DEMO COURTBOOKING")
print("="*60)

# ==================== 1. XOA DATA CU ====================
print("\n[1/6] Xoa data cu...")
Booking.objects.all().delete()
Favorite.objects.all().delete()
Court.objects.all().delete()
Promotion.objects.all().delete()
# Giu lai superuser va admin role
User.objects.exclude(is_superuser=True).exclude(role='admin').delete()
print(" OK - da xoa booking, favorite, court, promotion, user cu (giu superuser+admin)")

# ==================== 2. TAO TAI KHOAN ====================
print("\n[2/6] Tao tai khoan demo...")
player_demo = User.objects.create_user(
    username='player_demo', password='Demo@2026',
    email='player_demo@courtbooking.local',
    phone='0901234567', role='player',
    first_name='Nguyen Van', last_name='Demo'
)
player2 = User.objects.create_user(
    username='player2', password='Demo@2026',
    email='player2@courtbooking.local',
    phone='0907654321', role='player',
    first_name='Tran Hai', last_name='Anh'
)
owner_demo = User.objects.create_user(
    username='owner_demo', password='Demo@2026',
    email='owner_demo@courtbooking.local',
    phone='0912345678', role='owner',
    first_name='Pham Chu', last_name='San'
)
print(" OK - da tao 3 tai khoan: player_demo, player2, owner_demo (pass: Demo@2026)")

# ==================== 3. TAO SAN ====================
print("\n[3/6] Tao 6 san...")
court1 = Court.objects.create(
    name='Cum San Tennis Ngoai Giao Doan',
    court_type='tennis', district='hai_ba_trung',
    address='Khu Ngoai Giao Doan, Hai Ba Trung, Ha Noi',
    description='Mat san chat luong cao, den led day du, co khu thay do va cho ngoi cho.',
    price_per_hour=300000, owner=owner_demo, is_active=True
)
court2 = Court.objects.create(
    name='San Cau long Hoan Kiem',
    court_type='badminton', district='hoan_kiem',
    address='12 Pho Hang Bai, Hoan Kiem, Ha Noi',
    description='San trong nha, san go tieu chuan, it gio, anh sang tot.',
    price_per_hour=150000, owner=owner_demo, is_active=True
)
court3 = Court.objects.create(
    name='San Bong da mini Cau Giay',
    court_type='football', district='cau_giay',
    address='98 Tran Thai Tong, Cau Giay, Ha Noi',
    description='San co nhan tao 5 nguoi, co luoi chong bong bay ra ngoai, sach se.',
    price_per_hour=500000, owner=owner_demo, is_active=True
)
court4 = Court.objects.create(
    name='CLB Pickleball Dong Da',
    court_type='pickleball', district='dong_da',
    address='45 Tay Son, Dong Da, Ha Noi',
    description='San pickleball moi khai truong, mat san acrylic, co gan camera live.',
    price_per_hour=100000, owner=owner_demo, is_active=True
)
court5 = Court.objects.create(
    name='Nha thi dau Bong ro Thanh Xuan',
    court_type='basketball', district='thanh_xuan',
    address='234 Nguyen Trai, Thanh Xuan, Ha Noi',
    description='San go tieu chuan FIBA, co khan dai 200 cho, den led 1000W.',
    price_per_hour=250000, owner=owner_demo, is_active=True
)
court6 = Court.objects.create(
    name='San Tennis Ha Dong',
    court_type='tennis', district='ha_dong',
    address='15 Nguyen Trai, Ha Dong, Ha Noi',
    description='San tennis ngoai troi, mat cung, co ghe ngoi co dong.',
    price_per_hour=280000, owner=owner_demo, is_active=False 
)
print(" OK - da tao 6 san (5 active + 1 inactive de demo)")

# ==================== 4. TAO MA KHUYEN MAI ====================
print("\n[4/6] Tao 3 ma khuyen mai...")
Promotion.objects.create(
    code='SUMMER2026',
    description='Ma he 2026 - giam 15% cho moi don',
    discount_type='percent', discount_value=Decimal('15'),
    start_date=make_dt(2026, 6, 1, 0, 0),
    end_date=make_dt(2026, 7, 30, 23, 59),
    is_active=True
)
Promotion.objects.create(
    code='WELCOME50K',
    description='Khach moi - giam thang 50.000d',
    discount_type='flat', discount_value=Decimal('50000'),
    start_date=make_dt(2026, 6, 1, 0, 0),
    end_date=make_dt(2026, 12, 31, 23, 59),
    is_active=True
)
Promotion.objects.create(
    code='EXPIRED2025',
    description='Ma da het han (demo trang thai khong hoat dong)',
    discount_type='percent', discount_value=Decimal('20'),
    start_date=make_dt(2025, 1, 1, 0, 0),
    end_date=make_dt(2025, 12, 31, 23, 59),
    is_active=False
)
print(" OK - 2 ma active (SUMMER2026 15%, WELCOME50K 50k) + 1 het han")

# ==================== 5. TAO BOOKING ====================
print("\n[5/6] Tao 8 booking...")
TODAY = date.today() 

Booking.objects.create(
    court=court1, user=player_demo,
    date=TODAY - timedelta(days=6), start_time=time(9, 0), duration_hours=1,
    total_price=300000, status='confirmed'
)
Booking.objects.create(
    court=court2, user=player_demo,
    date=TODAY - timedelta(days=4), start_time=time(17, 0), duration_hours=1,
    total_price=150000, status='confirmed'
)
Booking.objects.create(
    court=court3, user=player_demo,
    date=TODAY - timedelta(days=3), start_time=time(20, 0), duration_hours=1,
    total_price=500000, status='confirmed'
)
Booking.objects.create(
    court=court4, user=player2,
    date=TODAY - timedelta(days=2), start_time=time(14, 0), duration_hours=1,
    total_price=100000, status='confirmed'
)
Booking.objects.create(
    court=court1, user=player2,
    date=TODAY - timedelta(days=2), start_time=time(18, 0), duration_hours=1,
    total_price=300000, status='confirmed'
)
Booking.objects.create(
    court=court5, user=player_demo,
    date=TODAY - timedelta(days=1), start_time=time(19, 0), duration_hours=1,
    total_price=250000, status='confirmed'
)
Booking.objects.create(
    court=court1, user=player_demo,
    date=TODAY + timedelta(days=1), start_time=time(20, 0), duration_hours=1,
    total_price=300000, status='pending'
)
Booking.objects.create(
    court=court1, user=player2,
    date=TODAY, start_time=time(15, 0), duration_hours=1,
    total_price=300000, status='confirmed'
)
print(" OK - 8 booking (7 confirmed + 1 pending)")

# ==================== 6. TAO FAVORITE ====================
print("\n[6/6] Tao san yeu thich...")
Favorite.objects.create(user=player_demo, court=court1)
Favorite.objects.create(user=player_demo, court=court3)
print(" OK - player_demo da yeu thich 2 san (Tennis NGD, Bong da CG)")

# ==================== TOM TAT ====================
print("\n" + "="*60)
print("SEED HOAN TAT")
print("="*60)
print(f"User: {User.objects.count()}")
print(f"Court: {Court.objects.count()} ({Court.objects.filter(is_active=True).count()} active)")
print(f"Booking: {Booking.objects.count()} ({Booking.objects.filter(status='confirmed').count()} confirmed, {Booking.objects.filter(status='pending').count()} pending)")
print(f"Promotion: {Promotion.objects.count()} ({Promotion.objects.filter(is_active=True).count()} active)")
print(f"Favorite: {Favorite.objects.count()}")
print()
print("TAI KHOAN DEMO (mat khau: Demo@2026):")
print(" - player_demo (Nguoi choi)")
print(" - player2 (Nguoi choi)")
print(" - owner_demo (Chu san)")
print(" - (admin: dung tai khoan da tao truoc)")
print()
print("MA GIAM GIA HOAT DONG:")
print(" - SUMMER2026 -> giam 15%")
print(" - WELCOME50K -> giam 50.000d")
print()
print(f"BLOCK SLOT TEST ANTI-OVERLAP:")
print(f" San Tennis NGD | {TODAY} | 15:00-16:00")
print(f" -> Khi demo co tinh dat slot nay -> bi chan.")
print()
print(f"SLOT TRONG DE DAT LIVE:")
print(f" San Tennis NGD | {TODAY} | 17:00 tro di -> trong.")
print("="*60)