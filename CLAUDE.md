# CLAUDE.md — DỰ ÁN COURTBOOKING

> File này được Claude Code đọc tự động mỗi lần chạy.
> Mọi prompt phải tuân theo các quy tắc dưới đây.

---

## 1. BỐI CẢNH DỰ ÁN

- **Tên**: CourtBooking — Website đặt lịch sân bóng đá / cầu lông / pickleball
- **Môn**: Lập trình ứng dụng — Học viện Ngân hàng — GV: TS. Triệu Thu Hương
- **Nhóm**: Nhóm 1 (5 thành viên) — Trưởng nhóm: Bách
- **Deadline**: 10/06/2026
- **Mục tiêu điểm**: A (9+)

---

## 2. RÀNG BUỘC TUYỆT ĐỐI (KHÔNG ĐƯỢC VI PHẠM)

Cô Hương chỉ dạy các kỹ thuật sau, và sẽ chấm điểm dựa trên việc nhóm có dùng đúng style này không. Code phải GIỐNG bài thực hành cô dạy để báo cáo nhìn quen thuộc và nhóm trả lời được câu hỏi của cô.

### 2.1. View: CHỈ DÙNG Function-Based View (FBV)

✅ ĐÚNG:
```python
def court_list(request):
    courts = Court.objects.all()
    return render(request, 'courts/court_list.html', {'courts': courts})
```

❌ SAI (không dùng):
```python
class CourtListView(ListView):  # KHÔNG ĐƯỢC
    model = Court
```

### 2.2. Form: CHỈ DÙNG ModelForm

✅ ĐÚNG:
```python
class CourtForm(forms.ModelForm):
    class Meta:
        model = Court
        fields = '__all__'
```

### 2.3. CRUD pattern (giống bài Product của cô)

Mỗi module CRUD phải có 4 view với tên:
- `<entity>_list` — xem danh sách
- `<entity>_create` — thêm mới
- `<entity>_update` — sửa
- `<entity>_delete` — xóa

Ví dụ: `court_list`, `court_create`, `court_update`, `court_delete`.

### 2.4. URL naming

```python
urlpatterns = [
    path('', views.court_list, name='court_list'),
    path('add/', views.court_create, name='court_create'),
    path('edit/<int:pk>/', views.court_update, name='court_update'),
    path('delete/<int:pk>/', views.court_delete, name='court_delete'),
]
```

### 2.5. Template path

```
courts/templates/courts/court_list.html
courts/templates/courts/court_form.html
```

Đường dẫn render: `render(request, 'courts/court_list.html', ...)`

### 2.6. Phân trang

Dùng `Paginator` với biến `page_obj` (giống bài phân trang sản phẩm):

```python
from django.core.paginator import Paginator

def court_list(request):
    court_list = Court.objects.all().order_by('-id')
    paginator = Paginator(court_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'courts/court_list.html', {'page_obj': page_obj})
```

### 2.7. Upload ảnh

```python
image = models.ImageField(upload_to='courts/')
```

Trong template:
```html
<form method="POST" enctype="multipart/form-data">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Lưu</button>
</form>
```

Trong view:
```python
form = CourtForm(request.POST, request.FILES)
```

### 2.8. Authentication

**Quan trọng**: Cô dạy session thủ công (`request.session['username']`). Tuy nhiên dự án này có 3 role nên DÙNG `django.contrib.auth` NHƯNG vẫn lưu thêm `role` vào session để check.

```python
# Trong login view
from django.contrib.auth import authenticate, login

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['role'] = user.role  # 'guest', 'player', 'admin'
            return redirect('home')
    return render(request, 'accounts/login.html')
```

Check role trong view:
```python
def admin_dashboard(request):
    if request.session.get('role') != 'admin':
        return redirect('login')
    # ... tiếp tục
```

### 2.9. Layout (giống bài layout của cô)

Tạo trong app chính (hoặc app `accounts`):
```
templates/
    partials/
        header.html
        footer.html
    base.html
```

Mỗi template con: `{% extends 'base.html' %}` rồi `{% block content %}...{% endblock %}`.

### 2.10. Bootstrap 5

Được phép dùng Bootstrap 5 (qua CDN) để giao diện đẹp, nhưng KHÔNG đổi cấu trúc template của cô. Chỉ thêm class vào HTML có sẵn.

CDN trong `base.html`:
```html
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
```

### 2.11. Comment

Comment tiếng Việt, viết hoa section như bài cô:
```python
# THÊM SÂN MỚI
def court_create(request):
    ...

# CẬP NHẬT SÂN
def court_update(request, pk):
    ...
```

### 2.12. KHÔNG dùng

- ❌ Class-based view
- ❌ Django REST Framework
- ❌ django-allauth, django-crispy-forms, hoặc thư viện ngoài
- ❌ Async view, signals tự viết, middleware tự viết
- ❌ TypeScript, React, Vue
- ❌ AJAX phức tạp (nếu cần thì dùng fetch đơn giản)
- ❌ Tailwind CSS (chỉ Bootstrap)

---

## 3. CẤU TRÚC THƯ MỤC DỰ ÁN

```
CourtBooking/
├── venv/                          # virtual environment (không commit)
├── courtbooking/                  # project chính
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                      # USER, đăng ký, đăng nhập
│   ├── models.py                  # User custom (extends AbstractUser, thêm role)
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   └── templates/
│       ├── base.html
│       ├── partials/
│       │   ├── header.html
│       │   └── footer.html
│       └── accounts/
│           ├── login.html
│           ├── register.html
│           └── profile.html
├── courts/                        # COURT, COURTTYPE, TIMESLOT, tìm kiếm
├── bookings/                      # BOOKING (logic chống trùng lịch)
├── payments/                      # PAYMENT giả lập
├── reviews/                       # REVIEW
├── promotions/                    # PROMOTION
├── media/                         # ảnh upload (không commit)
├── static/                        # css, js, ảnh tĩnh
├── db.sqlite3                     # database (không commit)
├── manage.py
├── requirements.txt
├── README.md
└── CLAUDE.md                      # file này
```

---

## 4. SCHEMA DATABASE (8 BẢNG ĐÃ CHỐT)

### 4.1. USER (kế thừa AbstractUser)
```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('guest', 'Khách'),
        ('player', 'Người chơi'),
        ('admin', 'Quản trị'),
    ]
    phone = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='player')

    def __str__(self):
        return self.username
```

Trong `settings.py` thêm: `AUTH_USER_MODEL = 'accounts.User'`

### 4.2. COURTTYPE
```python
# courts/models.py
class CourtType(models.Model):
    name = models.CharField(max_length=50)  # 'Bóng đá', 'Cầu lông', 'Pickleball'
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
```

### 4.3. COURT
```python
class Court(models.Model):
    courttype = models.ForeignKey(CourtType, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    price_per_hour = models.IntegerField()  # VND
    image = models.ImageField(upload_to='courts/')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
```

### 4.4. TIMESLOT
```python
class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"
```

### 4.5. BOOKING (QUAN TRỌNG NHẤT — có ràng buộc unique_together)
```python
# bookings/models.py
from django.db import models
from django.conf import settings
from courts.models import Court, TimeSlot
from promotions.models import Promotion

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ thanh toán'),
        ('confirmed', 'Đã xác nhận'),
        ('cancelled', 'Đã hủy'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    court = models.ForeignKey(Court, on_delete=models.CASCADE)
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    promotion = models.ForeignKey(Promotion, on_delete=models.SET_NULL, null=True, blank=True)
    booking_date = models.DateField()
    total_price = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('court', 'timeslot', 'booking_date')

    def __str__(self):
        return f"{self.user.username} - {self.court.name} - {self.booking_date}"
```

### 4.6. PAYMENT
```python
# payments/models.py
class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'Tiền mặt'),
        ('momo', 'MoMo (giả lập)'),
        ('banking', 'Chuyển khoản (giả lập)'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Chờ thanh toán'),
        ('success', 'Thành công'),
        ('failed', 'Thất bại'),
    ]
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
```

### 4.7. REVIEW
```python
# reviews/models.py
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    court = models.ForeignKey('courts.Court', on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1-5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

### 4.8. PROMOTION
```python
# promotions/models.py
class Promotion(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.IntegerField()  # 0-100
    valid_until = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code
```

---

## 5. LOGIC CHỐNG TRÙNG LỊCH (2 LỚP BẢO VỆ)

### Lớp 1: Code-level (kiểm tra trước khi save)
```python
def booking_create(request, court_id):
    if request.method == 'POST':
        court = get_object_or_404(Court, pk=court_id)
        timeslot_id = request.POST.get('timeslot')
        booking_date = request.POST.get('booking_date')

        # KIỂM TRA TRÙNG LỊCH
        exists = Booking.objects.filter(
            court=court,
            timeslot_id=timeslot_id,
            booking_date=booking_date,
            status__in=['pending', 'confirmed']
        ).exists()

        if exists:
            messages.error(request, 'Sân đã được đặt ở khung giờ này!')
            return redirect('booking_create', court_id=court_id)

        # TẠO BOOKING
        booking = Booking.objects.create(...)
        return redirect('payment', booking_id=booking.id)
    ...
```

### Lớp 2: Database-level (unique_together trong Meta)
Đã có trong model Booking ở trên.

---

## 6. ROUTING TỔNG (courtbooking/urls.py)

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('courts/', include('courts.urls')),
    path('bookings/', include('bookings.urls')),
    path('payments/', include('payments.urls')),
    path('reviews/', include('reviews.urls')),
    path('promotions/', include('promotions.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 7. QUY TẮC GIAO TIẾP VỚI CLAUDE CODE

Khi tôi (Bách) yêu cầu code, Claude phải:

1. **Đọc CLAUDE.md đầu tiên** — kiểm tra style, schema
2. **Hỏi rõ trước khi code lớn** — nếu task không rõ, hỏi lại
3. **Code TỪNG BƯỚC** — không tạo 10 file 1 lúc, làm từng module nhỏ
4. **Sau mỗi bước, hướng dẫn test** — `runserver` rồi vào URL nào
5. **Báo cáo gọn**: "Đã tạo X, Y. Bước tiếp theo: Z. Bạn test bằng cách: ..."
6. **Không tự ý thêm thư viện** — nếu cần lib mới, hỏi trước
7. **Comment tiếng Việt** trong code
8. **Khi gặp lỗi**: giải thích nguyên nhân + fix, không chỉ fix mù

---

## 8. CHECKLIST MỖI MODULE

Khi xong 1 module, kiểm tra đủ:

- [ ] Model có `__str__()` 
- [ ] Đăng ký vào `admin.py`
- [ ] Có form (ModelForm)
- [ ] Có 4 view CRUD
- [ ] URL đặt tên đúng convention
- [ ] Template extends base.html
- [ ] Phân quyền (role) check ở đầu view
- [ ] Test: thêm/sửa/xóa/list đều chạy
- [ ] Commit git: `git commit -m "Hoan thanh module <ten>"`
