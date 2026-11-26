from datetime import date, datetime, timedelta

from django import forms

from .models import CLOSE_HOUR, OPEN_HOUR, SLOT_MINUTES, Booking


# FORM ĐẶT SÂN (date, start_time, duration_hours được điền từ JS time-slot grid)
class BookingForm(forms.ModelForm):

    class Meta:
        model  = Booking
        # court, user, giá, status gán ở view — không để user nhập
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

        # GIỜ BẮT ĐẦU PHẢI ĐÚNG MỐC 30 PHÚT (chống sửa hidden input bằng F12)
        if start_time.minute % SLOT_MINUTES or start_time.second:
            raise forms.ValidationError('Giờ bắt đầu phải theo mốc 30 phút (VD 08:00, 08:30).')

        dt_new_start = datetime.combine(booking_date, start_time)
        dt_new_end   = dt_new_start + timedelta(hours=duration_hours)
        dt_open      = datetime.combine(booking_date, datetime.min.time()).replace(hour=OPEN_HOUR)
        dt_close     = datetime.combine(booking_date, datetime.min.time()).replace(hour=CLOSE_HOUR)

        # KHÔNG CHO ĐẶT NGÀY / GIỜ TRONG QUÁ KHỨ
        if booking_date < date.today():
            raise forms.ValidationError('Không thể đặt sân cho ngày đã qua.')
        if dt_new_start < datetime.now():
            raise forms.ValidationError('Không thể đặt khung giờ đã qua trong ngày hôm nay.')

        # PHẢI NẰM TRONG GIỜ MỞ CỬA (so sánh datetime nên không lỗi khi vắt qua nửa đêm)
        if dt_new_start < dt_open or dt_new_end > dt_close:
            raise forms.ValidationError(
                f'Sân chỉ mở từ {OPEN_HOUR:02d}:00 đến {CLOSE_HOUR:02d}:00. '
                f'Khung giờ bạn chọn kết thúc lúc {dt_new_end.strftime("%H:%M")}.'
            )

        # LỚP 1: KIỂM TRA GIAO NHAU VỚI CÁC ĐƠN CHƯA HUỶ (báo lỗi thân thiện cho người dùng)
        existing = Booking.objects.filter(
            court=self.court,
            date=booking_date,
        ).exclude(status='cancelled')
        if self.booking_id:
            existing = existing.exclude(pk=self.booking_id)

        # Điều kiện giao nhau: new_start < exist_end VÀ new_end > exist_start
        for booking in existing:
            dt_exist_start = datetime.combine(booking_date, booking.start_time)
            dt_exist_end   = dt_exist_start + timedelta(hours=booking.duration_hours)
            if dt_new_start < dt_exist_end and dt_new_end > dt_exist_start:
                raise forms.ValidationError(
                    f'Khung giờ này đã có người đặt ({dt_exist_start.strftime("%H:%M")} – '
                    f'{dt_exist_end.strftime("%H:%M")}). Vui lòng chọn giờ khác.'
                )

        return cleaned_data
