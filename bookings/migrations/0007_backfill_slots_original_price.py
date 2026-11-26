from datetime import datetime

from django.db import migrations

OPEN_HOUR, SLOT_MINUTES = 6, 30


def forwards(apps, schema_editor):
    Booking     = apps.get_model('bookings', 'Booking')
    BookingSlot = apps.get_model('bookings', 'BookingSlot')

    slots = []
    for b in Booking.objects.all():
        # GIÁ GỐC CỦA ĐƠN CŨ = thực thu + tiền giảm
        b.original_price = (b.total_price or 0) + (b.discount_amount or 0)
        b.save(update_fields=['original_price'])

        if b.status == 'cancelled':
            continue
        start = ((b.start_time.hour - OPEN_HOUR) * 60 + b.start_time.minute) // SLOT_MINUTES
        for i in range(start, start + b.duration_hours * 60 // SLOT_MINUTES):
            slots.append(BookingSlot(booking=b, court_id=b.court_id, date=b.date, slot=i))
    # Dữ liệu cũ có thể đã lỡ chồng giờ → bỏ qua slot trùng thay vì làm hỏng migrate
    BookingSlot.objects.bulk_create(slots, ignore_conflicts=True)


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0006_slot_lock_original_price'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
