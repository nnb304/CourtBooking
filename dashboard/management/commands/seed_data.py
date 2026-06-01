"""
Lệnh tạo dữ liệu demo cho CourtBooking.
Chạy: python manage.py seed_data
Reset: python manage.py seed_data --reset
"""

import io
import os
import random
import sys
from datetime import date, datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from bookings.models import Booking
from courts.models import Court
from payments.models import Payment
from promotions.models import Promotion
from reviews.models import Review

User = get_user_model()

# --- KHUNG GIỜ DEMO (8 slot × 2 tiếng) --------------------------------------
SLOT_START_TIMES = [
    time(6, 0),
    time(8, 0),
    time(10, 0),
    time(12, 0),
    time(14, 0),
    time(16, 0),
    time(18, 0),
    time(20, 0),
]

# --- DỮ LIỆU OWNER MỚI -------------------------------------------------------
OWNER_DATA = [
    {'username': 'chusan2', 'first_name': 'Hùng',  'last_name': 'Trần Đức',   'phone': '0911222333'},
    {'username': 'chusan3', 'first_name': 'Lan',   'last_name': 'Nguyễn Thị', 'phone': '0922333444'},
    {'username': 'chusan4', 'first_name': 'Tuấn',  'last_name': 'Phạm Anh',   'phone': '0933444555'},
]

# --- DỮ LIỆU PLAYER MỚI ------------------------------------------------------
PLAYER_DATA = [
    {'username': 'player_an',     'first_name': 'An',     'last_name': 'Nguyễn Văn',  'phone': '0912111222'},
    {'username': 'player_binh',   'first_name': 'Bình',   'last_name': 'Trần Quốc',   'phone': '0923222333'},
    {'username': 'player_cuong',  'first_name': 'Cường',  'last_name': 'Lê Đình',     'phone': '0934333444'},
    {'username': 'player_dung',   'first_name': 'Dũng',   'last_name': 'Phạm Minh',   'phone': '0945444555'},
    {'username': 'player_em',     'first_name': 'Em',     'last_name': 'Hoàng Thị',   'phone': '0956555666'},
    {'username': 'player_phuong', 'first_name': 'Phương', 'last_name': 'Vũ Thị',      'phone': '0967666777'},
    {'username': 'player_giang',  'first_name': 'Giang',  'last_name': 'Đặng Thị',    'phone': '0978777888'},
    {'username': 'player_huy',    'first_name': 'Huy',    'last_name': 'Bùi Công',    'phone': '0989888999'},
    {'username': 'player_khanh',  'first_name': 'Khánh',  'last_name': 'Đinh Thị',    'phone': '0990999000'},
    {'username': 'player_linh',   'first_name': 'Linh',   'last_name': 'Ngô Thị',     'phone': '0901000111'},
]

# --- DỮ LIỆU SÂN (13 sân, chia 4 owner) -------------------------------------
COURT_DATA = [
    # --- chusan1: 3 sân ---
    {
        'name': 'Sân bóng đá Mỹ Đình Star',
        'court_type': 'football',
        'district': 'nam_tu_liem',
        'address': '234 Lê Đức Thọ, Nam Từ Liêm, Hà Nội',
        'price': 350000,
        'owner_username': 'chusan1',
        'is_active': True,
        'description': (
            'Sân cỏ nhân tạo thế hệ mới, hệ thống đèn LED chiếu sáng đồng đều. '
            'Phòng thay đồ rộng rãi, sạch sẽ, có tủ khóa cá nhân. '
            'Gửi xe máy miễn phí, bãi đỗ ô tô ngay cổng.'
        ),
    },
    {
        'name': 'Sân cầu lông Cầu Giấy A',
        'court_type': 'badminton',
        'district': 'cau_giay',
        'address': '18 Dịch Vọng Hậu, Cầu Giấy, Hà Nội',
        'price': 120000,
        'owner_username': 'chusan1',
        'is_active': True,
        'description': (
            'Sân cầu lông tiêu chuẩn, sàn gỗ chống trơn chuẩn thi đấu. '
            'Hệ thống điều hòa mát mẻ, cho thuê vợt giá rẻ tại chỗ. '
            'Đặt online giảm 5%, mở cửa từ 6h–22h.'
        ),
    },
    {
        'name': 'Sân Pickleball Royal City',
        'court_type': 'pickleball',
        'district': 'thanh_xuan',
        'address': '72A Nguyễn Trãi, Thanh Xuân, Hà Nội',
        'price': 200000,
        'owner_username': 'chusan1',
        'is_active': True,
        'description': (
            'Sân pickleball trong nhà, sàn composite chất lượng cao, êm ái cho đầu gối. '
            'Khu vực ngồi chờ thoáng mát, căn-tin phục vụ nước uống và đồ ăn nhẹ. '
            'Huấn luyện viên hỗ trợ người mới học theo yêu cầu.'
        ),
    },
    # --- chusan2: 4 sân ---
    {
        'name': 'Sân bóng đá Thanh Xuân Star',
        'court_type': 'football',
        'district': 'thanh_xuan',
        'address': '56 Khương Trung, Thanh Xuân, Hà Nội',
        'price': 280000,
        'owner_username': 'chusan2',
        'is_active': True,
        'description': (
            'Sân 7 người cỏ nhân tạo cao cấp, bảo trì định kỳ hàng tháng. '
            'Có quán nước phục vụ sau trận, hệ thống đèn sáng chơi tối thoải mái. '
            'Đặt trước 2 tiếng được giữ chỗ không cần cọc.'
        ),
    },
    {
        'name': 'Sân cầu lông Đống Đa Pro',
        'court_type': 'badminton',
        'district': 'dong_da',
        'address': '9 Chùa Bộc, Đống Đa, Hà Nội',
        'price': 100000,
        'owner_username': 'chusan2',
        'is_active': True,
        'description': (
            'Hai sân cầu lông cạnh nhau, thích hợp nhóm đông thi đấu giao hữu. '
            'Phòng thay đồ có tủ khóa cá nhân, vòi tắm nóng lạnh. '
            'Mở cửa từ 6h00 đến 22h00 mỗi ngày kể cả lễ tết.'
        ),
    },
    {
        'name': 'Sân Pickleball Hà Đông Center',
        'court_type': 'pickleball',
        'district': 'ha_dong',
        'address': '120 Quang Trung, Hà Đông, Hà Nội',
        'price': 180000,
        'owner_username': 'chusan2',
        'is_active': True,
        'description': (
            'Sân pickleball outdoor thoáng mát, mái che chống nắng và mưa nhẹ. '
            'Dụng cụ cho thuê đầy đủ, phù hợp người mới tập. '
            'Bãi đỗ xe rộng rãi, gần chợ Hà Đông tiện mua sắm sau khi chơi.'
        ),
    },
    {
        'name': 'Sân bóng đá Hoàng Mai Arena',
        'court_type': 'football',
        'district': 'khac',
        'address': '203 Tam Trinh, Hoàng Mai, Hà Nội',
        'price': 300000,
        'owner_username': 'chusan2',
        'is_active': False,  # chờ admin duyệt
        'description': (
            'Sân 5 người và 7 người linh hoạt, cỏ nhân tạo nhập khẩu Châu Âu. '
            'Đang hoàn thiện cơ sở hạ tầng, sắp khai trương chính thức. '
            'Camera giám sát 24/7, bảo vệ thường trực cả ngày.'
        ),
    },
    # --- chusan3: 3 sân ---
    {
        'name': 'Sân cầu lông Hai Bà Trưng Olympic',
        'court_type': 'badminton',
        'district': 'hai_ba_trung',
        'address': '45 Lê Đại Hành, Hai Bà Trưng, Hà Nội',
        'price': 90000,
        'owner_username': 'chusan3',
        'is_active': True,
        'description': (
            'Sân cầu lông chuẩn Olympic, thảm nhựa PVC chuyên nghiệp không trơn. '
            'Phù hợp thi đấu câu lạc bộ hoặc luyện tập cá nhân. '
            'Huấn luyện viên cấp quốc gia hỗ trợ đặt lịch riêng.'
        ),
    },
    {
        'name': 'Sân Pickleball Tây Hồ Garden',
        'court_type': 'pickleball',
        'district': 'khac',
        'address': '67 Xuân La, Tây Hồ, Hà Nội',
        'price': 220000,
        'owner_username': 'chusan3',
        'is_active': True,
        'description': (
            'Không gian xanh mát bên hồ Tây, sân pickleball có view đẹp hiếm có. '
            'Bãi đỗ xe rộng rãi, quán cà phê ngay cạnh sân phục vụ cả ngày. '
            'Thích hợp chụp ảnh check-in sau khi chơi.'
        ),
    },
    {
        'name': 'Sân bóng đá Bắc Từ Liêm FC',
        'court_type': 'football',
        'district': 'bac_tu_liem',
        'address': '88 Phạm Văn Đồng, Bắc Từ Liêm, Hà Nội',
        'price': 320000,
        'owner_username': 'chusan3',
        'is_active': False,  # chờ admin duyệt
        'description': (
            'Sân bóng quy mô lớn, có khán đài mini sức chứa 200 khán giả. '
            'Đang xin cấp phép hoạt động, dự kiến mở cửa tháng tới. '
            'Camera giám sát và bảo vệ thường trực 24/7.'
        ),
    },
    # --- chusan4: 3 sân ---
    {
        'name': 'Sân Tennis Ba Đình Classic',
        'court_type': 'tennis',
        'district': 'khac',
        'address': '12 Hoàng Diệu, Ba Đình, Hà Nội',
        'price': 150000,
        'owner_username': 'chusan4',
        'is_active': True,
        'description': (
            'Sân tennis mặt cứng tiêu chuẩn ITF, được bảo trì định kỳ. '
            'Bóng và vợt cho thuê theo giờ, giá cả hợp lý. '
            'Gần công viên Thủ Lệ, không khí trong lành, thuận tiện di chuyển.'
        ),
    },
    {
        'name': 'Sân cầu lông Long Biên Sport',
        'court_type': 'badminton',
        'district': 'khac',
        'address': '31 Ngọc Lâm, Long Biên, Hà Nội',
        'price': 80000,
        'owner_username': 'chusan4',
        'is_active': True,
        'description': (
            'Giá thuê sân cạnh tranh nhất khu Long Biên, phù hợp sinh viên và gia đình. '
            'Mở cửa sớm từ 5h30, đặt sân linh hoạt từng giờ không cần đặt trước. '
            'Gần cầu Long Biên, view sông đẹp từ tầng thượng.'
        ),
    },
    {
        'name': 'Sân bóng đá Gia Lâm Champions',
        'court_type': 'football',
        'district': 'khac',
        'address': '5 Cổ Bi, Gia Lâm, Hà Nội',
        'price': 250000,
        'owner_username': 'chusan4',
        'is_active': False,  # chờ admin duyệt
        'description': (
            'Cụm 3 sân 5 người kết hợp, cho thuê trọn gói hoặc lẻ từng sân. '
            'Phù hợp tổ chức giải đấu nội bộ công ty, có thể đặt tiệc sau trận. '
            'Đang chờ phê duyệt, sắp đi vào hoạt động.'
        ),
    },
]

# --- DỮ LIỆU KHUYẾN MẠI ------------------------------------------------------
PROMO_DATA = [
    {
        'code': 'GIAM10',
        'description': 'Giảm 10% cho tất cả đơn đặt sân',
        'discount_type': 'percent',
        'discount_value': 10,
        'start_date': datetime(2025, 1, 1),
        'end_date': datetime(2026, 12, 31),
        'is_active': True,
    },
    {
        'code': 'GIAM20',
        'description': 'Giảm 20% cuối tuần',
        'discount_type': 'percent',
        'discount_value': 20,
        'start_date': datetime(2025, 6, 1),
        'end_date': datetime(2026, 12, 31),
        'is_active': True,
    },
    {
        'code': 'NEWUSER',
        'description': 'Ưu đãi 15% cho khách lần đầu đặt sân',
        'discount_type': 'percent',
        'discount_value': 15,
        'start_date': datetime(2025, 1, 1),
        'end_date': datetime(2026, 11, 30),
        'is_active': True,
    },
    {
        'code': 'HE2024',
        'description': 'Khuyến mãi hè 2024 — đã hết hạn',
        'discount_type': 'percent',
        'discount_value': 10,
        'start_date': datetime(2024, 6, 1),
        'end_date': datetime(2024, 8, 31),
        'is_active': False,
    },
    {
        'code': 'TET2024',
        'description': 'Siêu ưu đãi Tết 2024 — đã hết hạn',
        'discount_type': 'percent',
        'discount_value': 25,
        'start_date': datetime(2024, 1, 1),
        'end_date': datetime(2024, 2, 29),
        'is_active': False,
    },
]

# --- COMMENT ĐÁNH GIÁ THỰC TẾ ------------------------------------------------
REVIEW_COMMENTS = [
    'Sân đẹp, sạch sẽ, rất đáng tiền!',
    'Nhân viên thân thiện, phục vụ nhiệt tình.',
    'Giá hợp lý so với mặt bằng khu vực.',
    'Sân hơi cũ nhưng vẫn chấp nhận được, sẽ cải thiện hơn.',
    'Đèn sáng đủ, chơi tối rất thoải mái, không bị chói mắt.',
    'Chắc chắn sẽ quay lại lần sau, trải nghiệm tốt!',
    'Chỗ gửi xe hơi chật, cần mở rộng thêm.',
    'Phòng thay đồ sạch sẽ, có tủ khóa cá nhân tiện lợi.',
    'Đặt sân online rất tiện, xác nhận nhanh chóng.',
    'Sân rộng rãi, thoáng mát, thích hợp chơi buổi sáng sớm.',
    'Mặt sân tốt, không trơn kể cả khi trời mưa phùn.',
    'Giá buổi tối hơi cao so với ban ngày nhưng chất lượng xứng đáng.',
    'Bãi đỗ xe rộng, không lo tắc nghẽn kể cả giờ cao điểm.',
    'Cơ sở vật chất hiện đại, cảm giác chuyên nghiệp.',
    'Dịch vụ thuê vợt và bóng tại chỗ rất tiện lợi cho khách lần đầu.',
]

# --- USERNAME ĐƯỢC BẢO VỆ, KHÔNG XOÁ ----------------------------------------
PROTECTED_USERNAMES = {'nhom1', 'chusan1', 'test1'}


class Command(BaseCommand):
    help = 'Tạo dữ liệu demo cho CourtBooking (seed_data)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Xoá data demo cũ trước khi tạo lại',
        )

    def handle(self, *args, **options):
        # Đảm bảo stdout hỗ trợ UTF-8 trên Windows
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')

        if options['reset']:
            if not self._confirm_reset():
                self.stdout.write('Huỷ thao tác. Không có gì bị xoá.')
                return
            self._do_reset()

        self._seed_users()
        self._seed_courts()
        self._seed_promotions()
        self._seed_bookings()
        self._seed_payments()
        self._seed_reviews()
        self._print_summary()

    # --- XÁC NHẬN TRƯỚC KHI RESET --------------------------------------------
    def _confirm_reset(self):
        self.stdout.write(self.style.WARNING(
            '\nSẽ xoá: Booking/Payment/Review của sân seed'
            ' + Court của chusan2/3/4'
            ' + User player_*/chusan2/3/4.'
            '\nGIỮ NGUYÊN: nhom1, chusan1, test1 và dữ liệu của họ.\n'
        ))
        try:
            answer = input('Chắc chắn? (y/N): ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            return False
        return answer == 'y'

    # --- XOÁ DATA DEMO CŨ ----------------------------------------------------
    def _do_reset(self):
        seed_usernames = (
            {d['username'] for d in OWNER_DATA} |
            {d['username'] for d in PLAYER_DATA}
        ) - PROTECTED_USERNAMES

        seed_users  = User.objects.filter(username__in=seed_usernames)
        seed_courts = Court.objects.filter(
            owner__username__in=[d['username'] for d in OWNER_DATA]
        )

        # XOÁ THEO THỨ TỰ FK ĐỂ TRÁNH LỖI INTEGRITY
        Payment.objects.filter(booking__court__in=seed_courts).delete()
        Review.objects.filter(court__in=seed_courts).delete()
        Booking.objects.filter(court__in=seed_courts).delete()

        # Xoá booking/review của seed players trên các sân còn lại
        Payment.objects.filter(booking__user__in=seed_users).delete()
        Review.objects.filter(user__in=seed_users).delete()
        Booking.objects.filter(user__in=seed_users).delete()

        seed_courts.delete()
        seed_users.delete()
        Promotion.objects.filter(code__in=[p['code'] for p in PROMO_DATA]).delete()

        self.stdout.write(self.style.SUCCESS('[OK] Đã xoá data demo cũ.\n'))

    # --- TẠO USERS -----------------------------------------------------------
    def _seed_users(self):
        created = 0

        for d in OWNER_DATA:
            if d['username'] in PROTECTED_USERNAMES:
                continue
            user, is_new = User.objects.get_or_create(
                username=d['username'],
                defaults={
                    'first_name': d['first_name'],
                    'last_name':  d['last_name'],
                    'phone':      d['phone'],
                    'role':       'owner',
                    'email':      f"{d['username']}@demo.vn",
                },
            )
            if is_new:
                user.set_password('123456')
                user.save()
                created += 1

        for d in PLAYER_DATA:
            user, is_new = User.objects.get_or_create(
                username=d['username'],
                defaults={
                    'first_name': d['first_name'],
                    'last_name':  d['last_name'],
                    'phone':      d['phone'],
                    'role':       'player',
                    'email':      f"{d['username']}@demo.vn",
                },
            )
            if is_new:
                user.set_password('123456')
                user.save()
                created += 1

        self.stdout.write(f'[OK] Da tao {created} users moi (3 owners + 10 players).')

    # --- TẠO COURTS ----------------------------------------------------------
    def _seed_courts(self):
        # SCAN MEDIA/COURTS ĐỂ LẤY DANH SÁCH ẢNH SẴN CÓ
        media_courts_dir = os.path.join('media', 'courts')
        image_files = []
        if os.path.isdir(media_courts_dir):
            image_files = [
                f for f in os.listdir(media_courts_dir)
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
            ]

        if not image_files:
            self.stdout.write(self.style.WARNING(
                '[!] Không tìm thấy ảnh trong media/courts/.\n'
                '  Sân sẽ được tạo không có ảnh.\n'
                '  Để fix: copy vài file .jpg vào thư mục media/courts/\n'
                '  rồi chạy lại: python manage.py seed_data --reset'
            ))

        created = 0
        for d in COURT_DATA:
            # BỎ QUA NẾU SÂN CÙNG TÊN ĐÃ TỒN TẠI (tránh duplicate khi chạy lại)
            if Court.objects.filter(name=d['name']).exists():
                continue

            owner = User.objects.filter(username=d['owner_username']).first()
            if not owner:
                self.stdout.write(self.style.WARNING(
                    f"  Bo qua san '{d['name']}': khong tim thay owner '{d['owner_username']}'."
                ))
                continue

            # GÁN ẢNH RANDOM NẾU CÓ, ĐỂ TRỐNG NẾU KHÔNG CÓ
            image_value = None
            if image_files:
                image_value = f"courts/{random.choice(image_files)}"

            Court.objects.create(
                name=d['name'],
                court_type=d['court_type'],
                district=d['district'],
                address=d['address'],
                description=d['description'],
                price_per_hour=d['price'],
                is_active=d['is_active'],
                owner=owner,
                image=image_value,
            )
            created += 1

        self.stdout.write(f'[OK] Đã tạo {created} sân.')

    # --- TẠO PROMOTIONS ------------------------------------------------------
    def _seed_promotions(self):
        created = 0
        for d in PROMO_DATA:
            _, is_new = Promotion.objects.get_or_create(
                code=d['code'],
                defaults={
                    'description':    d['description'],
                    'discount_type':  d['discount_type'],
                    'discount_value': d['discount_value'],
                    'start_date':     d['start_date'],
                    'end_date':       d['end_date'],
                    'is_active':      d['is_active'],
                },
            )
            if is_new:
                created += 1
        self.stdout.write(f'[OK] Đã tạo {created} mã khuyến mãi.')

    # --- TẠO BOOKINGS --------------------------------------------------------
    def _seed_bookings(self):
        players = list(User.objects.filter(role='player'))

        # KIỂM TRA: NẾU SEED PLAYERS ĐÃ CÓ BOOKING THÌ SKIP
        if players and Booking.objects.filter(user__in=players).count() > 20:
            self.stdout.write(self.style.WARNING(
                'Seed players da co nhieu booking (>20). Dung --reset neu muon tao lai.'
            ))
            return

        active_courts = list(Court.objects.filter(is_active=True))
        active_promos = list(Promotion.objects.filter(is_active=True))

        if not active_courts:
            self.stdout.write(self.style.WARNING('Không có sân active để tạo bookings.'))
            return
        if not players:
            self.stdout.write(self.style.WARNING('Không có player để tạo bookings.'))
            return

        today = date.today()

        # NẠP (court_id, date, start_time) ĐÃ CÓ TRONG DB ĐỂ TRÁNH TRÙNG
        occupied = set()
        for b in Booking.objects.values('court_id', 'date', 'start_time'):
            occupied.add((b['court_id'], str(b['date']), str(b['start_time'])))

        TARGET  = 50   # số booking muốn tạo
        created = 0
        attempts = 0

        while created < TARGET and attempts < TARGET * 15:
            attempts += 1

            court   = random.choice(active_courts)
            player  = random.choice(players)
            delta   = random.randint(-21, 14)
            bk_date = today + timedelta(days=delta)
            start_t = random.choice(SLOT_START_TIMES)

            slot_key = (court.id, str(bk_date), str(start_t))
            if slot_key in occupied:
                continue
            occupied.add(slot_key)

            # PHÂN PHỐI TRẠNG THÁI THEO NGÀY
            if bk_date < today:
                status = random.choices(
                    ['confirmed', 'cancelled'],
                    weights=[85, 15],
                )[0]
            else:
                status = random.choices(
                    ['pending', 'confirmed', 'cancelled'],
                    weights=[30, 55, 15],
                )[0]

            # TÍNH GIÁ (2 giờ/slot)
            order_total     = int(court.price_per_hour) * 2
            promo           = None
            discount_amount = 0

            # 30% CONFIRMED ÁP PROMO
            if status == 'confirmed' and active_promos and random.random() < 0.30:
                promo = random.choice(active_promos)
                if promo.discount_type == 'percent':
                    discount_amount = int(order_total * promo.discount_value / 100)
                else:
                    discount_amount = min(int(promo.discount_value), order_total)

            Booking.objects.create(
                court=court,
                user=player,
                date=bk_date,
                start_time=start_t,
                duration_hours=2,
                promotion=promo,
                discount_amount=discount_amount,
                total_price=order_total - discount_amount,
                status=status,
            )
            created += 1

        self.stdout.write(f'[OK] Đã tạo {created} bookings.')

    # --- TẠO PAYMENTS --------------------------------------------------------
    def _seed_payments(self):
        created  = 0
        methods  = ['cash', 'momo', 'banking']

        # CONFIRMED → payment success
        confirmed_without_payment = (
            Booking.objects.filter(status='confirmed')
            .exclude(payment__isnull=False)
        )
        for booking in confirmed_without_payment:
            offset_min = random.randint(5, 120)
            paid_at    = datetime.now() - timedelta(
                days=random.randint(0, 20),
                minutes=offset_min,
            )
            Payment.objects.create(
                booking=booking,
                method=random.choice(methods),
                status='success',
                paid_at=paid_at,
            )
            created += 1

        # CANCELLED → 50% có payment failed
        cancelled_without_payment = (
            Booking.objects.filter(status='cancelled')
            .exclude(payment__isnull=False)
        )
        for booking in cancelled_without_payment:
            if random.random() < 0.5:
                Payment.objects.create(
                    booking=booking,
                    method=random.choice(methods),
                    status='failed',
                    paid_at=None,
                )
                created += 1

        self.stdout.write(f'[OK] Đã tạo {created} payments.')

    # --- TẠO REVIEWS ---------------------------------------------------------
    def _seed_reviews(self):
        created = 0
        today   = date.today()

        # CHỈ LẤY BOOKING CONFIRMED QUÁ KHỨ
        past_confirmed = list(
            Booking.objects.filter(status='confirmed', date__lt=today)
            .select_related('user', 'court')
        )

        # (user_id, court_id) ĐÃ CÓ REVIEW
        existing_pairs = set(
            Review.objects.values_list('user_id', 'court_id')
        )

        random.shuffle(past_confirmed)

        for booking in past_confirmed:
            # ~50% BOOKING QUÁ KHỨ CÓ REVIEW
            if random.random() > 0.50:
                continue

            pair = (booking.user_id, booking.court_id)
            if pair in existing_pairs:
                continue
            existing_pairs.add(pair)

            # PHÂN PHỐI RATING: 70% 4-5 sao, 25% 3 sao, 5% 1-2 sao
            r = random.random()
            if r < 0.70:
                rating = random.choice([4, 5])
            elif r < 0.95:
                rating = 3
            else:
                rating = random.choice([1, 2])

            Review.objects.create(
                court=booking.court,
                user=booking.user,
                rating=rating,
                comment=random.choice(REVIEW_COMMENTS),
            )
            created += 1

        self.stdout.write(f'[OK] Đã tạo {created} reviews.')

    # --- IN TỔNG KẾT ---------------------------------------------------------
    def _print_summary(self):
        total_courts    = Court.objects.count()
        active_courts   = Court.objects.filter(is_active=True).count()
        pending_courts  = Court.objects.filter(is_active=False).count()
        total_bookings  = Booking.objects.count()
        cnt_confirmed   = Booking.objects.filter(status='confirmed').count()
        cnt_pending_bk  = Booking.objects.filter(status='pending').count()
        cnt_cancelled   = Booking.objects.filter(status='cancelled').count()

        self.stdout.write('\n' + '-' * 44)
        self.stdout.write(self.style.SUCCESS('  TỔNG KẾT DỮ LIỆU DEMO'))
        self.stdout.write('-' * 44)
        self.stdout.write(f'  Users       : {User.objects.count()}')
        self.stdout.write(
            f'  Courts      : {total_courts} '
            f'(active: {active_courts}, pending: {pending_courts})'
        )
        self.stdout.write(
            f'  Bookings    : {total_bookings} '
            f'(confirmed: {cnt_confirmed}, '
            f'pending: {cnt_pending_bk}, '
            f'cancelled: {cnt_cancelled})'
        )
        self.stdout.write(f'  Payments    : {Payment.objects.count()}')
        self.stdout.write(f'  Reviews     : {Review.objects.count()}')
        self.stdout.write(f'  Promotions  : {Promotion.objects.count()}')
        self.stdout.write('-' * 44)
        self.stdout.write(
            self.style.SUCCESS(
                '  Đăng nhập: username / password 123456\n'
                '  Owners: chusan1..4 | Players: player_an..linh'
            )
        )
        self.stdout.write('-' * 44 + '\n')
