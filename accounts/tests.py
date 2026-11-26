from django.test import TestCase

# Create your tests here.


from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import User


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ActivationTests(TestCase):
    def _register(self):
        return self.client.post(reverse('accounts:register'), {
            'username': 'newbie', 'email': 'newbie@example.com', 'phone': '',
            'password1': 'Matkhau123!', 'password2': 'Matkhau123!', 'role': 'player',
        })

    def test_register_sends_email_and_user_inactive(self):
        self._register()
        user = User.objects.get(username='newbie')
        self.assertFalse(user.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/accounts/activate/', mail.outbox[0].body)

    def test_activation_link_activates(self):
        self._register()
        link = [w for w in mail.outbox[0].body.split() if '/accounts/activate/' in w][0]
        self.client.get(link.replace('http://testserver', ''))
        self.assertTrue(User.objects.get(username='newbie').is_active)
        self.assertTrue(self.client.login(username='newbie', password='Matkhau123!'))

    def test_login_before_activation_resends(self):
        self._register()
        self.client.post(reverse('accounts:login'), {'username': 'newbie', 'password': 'Matkhau123!'})
        self.assertEqual(len(mail.outbox), 2)

    def test_duplicate_email_rejected(self):
        self._register()
        self.client.post(reverse('accounts:register'), {
            'username': 'other', 'email': 'NEWBIE@example.com',
            'password1': 'Matkhau123!', 'password2': 'Matkhau123!',
        })
        self.assertFalse(User.objects.filter(username='other').exists())
