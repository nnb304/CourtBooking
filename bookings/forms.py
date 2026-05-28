from datetime import date, datetime, timedelta
from django import forms
from .models import Booking


# FORM ĐẶT SÂN (date, start_time, duration_hours được điền từ JS time-slot grid)
class BookingForm(forms.ModelForm):

    class Meta:
        model  = Booking
        # court, user, total_price, status gán ở view — không để user nhập
        fields = ['date', 'start_time', 'duration_hours']
        widgets = {
            'date':           forms.HiddenInput(),
            'start_time':     forms.HiddenInput(),
            'duration_hours': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        # view truyền court vào để clean() dùng kiểm tra trùng lịch
        self.court = kwargs.pop('court')
        # booking_id dùng khi chỉnh sửa — bỏ qua chính booking đó khi check trùng
        self.booking_id = kwargs.pop('booking_id', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        booking_date   = cleaned_data.get('date')
        start_time     = cleaned_data.get('start_time')
        duration_hours = cleaned_data.get('duration_hours')

        # NẾU CÁC FIELD BẮT BUỘC CHƯA HỢP LỆ THÌ BỎ QUA (tránh lỗi khi tính toán)
        if not (booking_date and start_time and duration_hours):
            return cleaned_data

        # KHÔNG CHO ĐẶT NGÀY TRONG QUÁ KHỨ
        if booking_date < date.today():
            raise forms.ValidationError('Không thể đặt sân cho ngày đã qua.')

        # TÍNH GIỜ KẾT THÚC CỦA ĐƠN MỚI
        dt_new_start = datetime.combine(booking_date, start_time)
        dt_new_end   = dt_new_start + timedelta(hours=duration_hours)
        new_start    = dt_new_start.time()
        new_end      = dt_new_end.time()

        # LẤY CÁC BOOKING CÙNG SÂN + CÙNG NGÀY + CHƯA HUỶ
        existing = Booking.objects.filter(
            court=self.court,
            date=booking_date,
        ).exclude(status='cancelled')

        # BỎ QUA CHÍNH ĐƠN ĐANG SỬA (nếu là update)
        if self.booking_id:
            existing = existing.exclude(pk=self.booking_id)

        # KIỂM TRA GIAO NHAU: [new_start, new_end) ∩ [exist_start, exist_end) ≠ ∅
        # Điều kiện giao nhau: new_start < exist_end VÀ new_end > exist_start
        for booking in existing:
            exist_start = booking.start_time
            dt_exist    = datetime.combine(booking_date, exist_start)
            exist_end   = (dt_exist + timedelta(hours=booking.duration_hours)).time()

            if new_start < exist_end and new_end > exist_start:
                raise forms.ValidationError(
                    f'Khung giờ này đã có người đặt ({exist_start.strftime("%H:%M")} – '
                    f'{exist_end.strftime("%H:%M")}). Vui lòng chọn giờ khác.'
                )

        return cleaned_data
