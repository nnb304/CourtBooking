from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # COURTS trước: trang chủ '/' nằm ở đây
    path('', include('courts.urls')),
    # ACCOUNTS: đăng nhập, đăng ký, profile
    path('accounts/', include('accounts.urls')),
    path('bookings/', include('bookings.urls')),
    path('payments/', include('payments.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('reviews/', include('reviews.urls')),
    path('promotions/', include('promotions.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
