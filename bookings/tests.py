from datetime import date, datetime, time, timedelta

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from courts.models import Court

from .forms import BookingForm
from .models import HOLD_MINUTES, Booking, BookingSlot, expire_stale_pending

TOMORROW = date.today() + timedelta(days=1)


class BookingLogicTests(TestCase):
    def setUp(self):
        self.owner  = User.objects.create_user('owner', password='x', role='owner')
        self.player = User.objects.create_user('player', password='x', role='player',
                                               first_name='An', last_name='Nguyen', phone='0900000000')
        self.court  = Court.objects.create(name='San A', court_type='badminton', address='HN',
                                           price_per_hour=100000, owner=self.owner)

    def _book(self, start, hours, status='pending'):
        b = Booking.objects.create(court=self.court, user=self.player, date=TOMORROW,
                                   start_time=start, duration_hours=hours,
                                   original_price=100000 * hours, total_price=100000 * hours, status=status)
        b.reserve_slots()
        return b

    def _form(self, start, hours, day=TOMORROW):
        return BookingForm({'date': day, 'start_time': start, 'duration_hours': hours}, court=self.court)

    # LỚP 1
    def test_form_rejects_overlap_with_different_start(self):
        self._book(time(8, 0), 2)
        self.assertFalse(self._form('09:00', 1).is_valid())

    def test_form_allows_adjacent_slot(self):
        self._book(time(8, 0), 2)
        self.assertTrue(self._form('10:00', 1).is_valid())

    def test_form_rejects_past_closing_time(self):
        self.assertFalse(self._form('21:00', 4).is_valid())
        self.assertTrue(self._form('20:00', 2).is_valid())

    def test_form_rejects_before_opening_and_odd_minutes(self):
        self.assertFalse(self._form('05:00', 1).is_valid())
        self.assertFalse(self._form('08:15', 1).is_valid())

    # LỚP 2: 2 request cùng qua được Lớp 1 rồi cùng lưu → DB chặn người sau
    def test_db_blocks_overlapping_race(self):
        self._book(time(8, 0), 2)
        b2 = Booking.objects.create(court=self.court, user=self.player, date=TOMORROW,
                                    start_time=time(9, 0), duration_hours=1, total_price=1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            b2.reserve_slots()

    def test_cancelled_slot_can_be_rebooked(self):
        b = self._book(time(8, 0), 2)
        b.cancel()
        self.assertEqual(BookingSlot.objects.count(), 0)
        self._book(time(8, 0), 2)   # không lỗi

    def test_stale_pending_is_released(self):
        b = self._book(time(8, 0), 1)
        Booking.objects.filter(pk=b.pk).update(created_at=datetime.now() - timedelta(minutes=HOLD_MINUTES + 1))
        expire_stale_pending()
        b.refresh_from_db()
        self.assertEqual(b.status, 'cancelled')
        self.assertTrue(self._form('08:00', 1).is_valid())

    # VIEW: lưu giá gốc + áp mã
    def test_create_view_stores_original_price(self):
        self.client.login(username='player', password='x')
        r = self.client.post(reverse('bookings:booking_create', args=[self.court.pk]),
                             {'date': TOMORROW, 'start_time': '08:00', 'duration_hours': 2})
        self.assertEqual(r.status_code, 302)
        b = Booking.objects.get()
        self.assertEqual(b.original_price, 200000)
        self.assertEqual(b.slots.count(), 4)

    # QUYỀN: owner list dựa vào role thật, không dựa vào session
    def test_owner_list_requires_owner_role(self):
        self.client.login(username='player', password='x')
        s = self.client.session; s['role'] = 'owner'; s.save()
        r = self.client.get(reverse('bookings:owner_booking_list'))
        self.assertEqual(r.status_code, 302)

    def test_owner_sees_customer_and_prices(self):
        self._book(time(8, 0), 2, status='confirmed')
        self.client.login(username='owner', password='x')
        r = self.client.get(reverse('bookings:owner_booking_list'))
        self.assertContains(r, '0900000000')
        self.assertContains(r, 'Giá gốc')
