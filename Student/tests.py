from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


class UserManagementTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='siteadmin',
            email='admin@example.com',
            password='V3ry-Strong-Admin-Passphrase!',
        )
        self.client.force_login(self.admin)

    def test_dashboard_shows_user_totals_and_accounts(self):
        User.objects.create_user(username='studentuser', password='V3ry-Strong-User-Passphrase!')

        response = self.client.get(reverse('user_management'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user_count'], 2)
        self.assertContains(response, 'studentuser')

    def test_regular_user_cannot_open_dashboard_or_manage_accounts(self):
        regular_user = User.objects.create_user(
            username='studentuser',
            password='V3ry-Strong-User-Passphrase!',
        )
        self.client.force_login(regular_user)

        self.assertEqual(self.client.get(reverse('user_management')).status_code, 403)
        self.assertEqual(
            self.client.post(
                reverse('manage_user', args=[self.admin.pk]),
                {'action': 'deactivate'},
            ).status_code,
            403,
        )

    def test_anonymous_user_is_redirected_to_login(self):
        self.client.logout()

        response = self.client.get(reverse('user_management'))

        self.assertRedirects(
            response,
            f"{reverse('login_page')}?next={reverse('user_management')}",
        )

    def test_superuser_can_create_user_with_staff_role(self):
        response = self.client.post(
            reverse('user_management'),
            {
                'username': 'newstaff',
                'email': 'staff@example.com',
                'password1': 'V3ry-Strong-Staff-Passphrase!',
                'password2': 'V3ry-Strong-Staff-Passphrase!',
                'role': 'staff',
            },
        )

        created_user = User.objects.get(username='newstaff')
        self.assertRedirects(response, reverse('user_management'))
        self.assertTrue(created_user.is_staff)
        self.assertFalse(created_user.is_superuser)

    def test_admin_can_change_role_activate_and_delete_other_users(self):
        managed_user = User.objects.create_user(
            username='managed',
            password='V3ry-Strong-Managed-Passphrase!',
        )

        response = self.client.post(
            reverse('manage_user', args=[managed_user.pk]),
            {'action': 'role', 'role': 'superuser'},
        )
        self.assertRedirects(response, reverse('user_management'))
        managed_user.refresh_from_db()
        self.assertTrue(managed_user.is_staff)
        self.assertTrue(managed_user.is_superuser)

        self.client.post(
            reverse('manage_user', args=[managed_user.pk]),
            {'action': 'deactivate'},
        )
        managed_user.refresh_from_db()
        self.assertFalse(managed_user.is_active)

        self.client.post(
            reverse('manage_user', args=[managed_user.pk]),
            {'action': 'delete'},
        )
        self.assertFalse(User.objects.filter(pk=managed_user.pk).exists())

    def test_admin_cannot_remove_or_delete_self(self):
        for action in ('deactivate', 'delete', 'role'):
            data = {'action': action, 'role': 'user'}
            response = self.client.post(
                reverse('manage_user', args=[self.admin.pk]),
                data,
            )
            self.assertRedirects(response, reverse('user_management'))
            self.admin.refresh_from_db()
            self.assertTrue(self.admin.is_active)
            self.assertTrue(self.admin.is_superuser)
            self.assertTrue(User.objects.filter(pk=self.admin.pk).exists())

    def test_admin_can_manage_another_superuser_without_losing_access(self):
        actions = (
            {'action': 'deactivate'},
            {'action': 'role', 'role': 'staff'},
            {'action': 'delete'},
        )
        other_admin = User.objects.create_superuser(
            username='otheradmin',
            email='other@example.com',
            password='V3ry-Strong-Other-Admin-Passphrase!',
        )

        response = self.client.post(
            reverse('manage_user', args=[other_admin.pk]),
            {'action': 'deactivate'},
        )
        self.assertRedirects(response, reverse('user_management'))
        other_admin.refresh_from_db()
        self.assertFalse(other_admin.is_active)

        self.client.post(
            reverse('manage_user', args=[other_admin.pk]),
            {'action': 'activate'},
        )
        self.client.post(
            reverse('manage_user', args=[other_admin.pk]),
            actions[1],
        )
        other_admin.refresh_from_db()
        self.assertTrue(other_admin.is_active)
        self.assertFalse(other_admin.is_superuser)
        self.assertTrue(User.objects.filter(pk=self.admin.pk, is_superuser=True).exists())

        self.client.post(
            reverse('manage_user', args=[other_admin.pk]),
            actions[2],
        )
        self.assertFalse(User.objects.filter(pk=other_admin.pk).exists())

    def test_user_actions_reject_get_requests(self):
        response = self.client.get(reverse('manage_user', args=[self.admin.pk]))

        self.assertEqual(response.status_code, 405)
