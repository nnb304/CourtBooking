from django.test import TestCase

# Create your tests here.


from datetime import date, time, timedelta

from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import User
from bookings.models import Booking
from courts.models import Court


class VietQRTests(TestCase):
    def setUp(self):
        self.user  = User.objects.create_user('p', password='x', role='player')
        court      = Court.objects.create(name='S', court_type='tennis', address='HN', price_per_hour=150000)
        self.b     = Booking.objects.create(court=court, user=self.user, date=date.today() + timedelta(days=1),
                                            start_time=time(8, 0), duration_hours=1, total_price=150000)
        self.client.login(username='p', password='x')

    @override_settings(VIETQR_BANK_ID='DEMO', VIETQR_ACCOUNT_NO='000', VIETQR_ACCOUNT_NAME='TEST')
    def test_qr_has_amount_and_note(self):
        r = self.client.get(reverse('payments:payment_process', args=[self.b.pk]))
        self.assertContains(r, 'img.vietqr.io/image/DEMO-000-compact2.png?amount=150000')
        self.assertContains(r, f'CB{self.b.pk}')

    def test_banking_confirm_succeeds(self):
        self.client.post(reverse('payments:payment_process', args=[self.b.pk]), {'method': 'banking'})
        self.b.refresh_from_db()
        self.assertEqual(self.b.status, 'confirmed')
