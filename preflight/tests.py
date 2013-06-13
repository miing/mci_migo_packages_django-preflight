# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).
import sys
try:
    from unittest import skipIf
except ImportError:
    from unittest2 import skipIf  # NOQA

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.test import TestCase
from django.template import RequestContext
from django.template.loader import render_to_string
from mock import (
    Mock,
    patch,
)

from cStringIO import StringIO
from pyquery import PyQuery

from . import Preflight
from .models import (
    Application,
    Check,
    REGISTRY,
    authenticate,
    gather_checks,
    gather_switches,
    gather_gargoyle,
    gather_settings,
    gather_versions,
)
from preflight.conf import BASE_TEMPLATE, TABLE_CLASS
from preflight.views import allow_basic_auth


class CheckTestCase(TestCase):

    def setUp(self):
        self.exception = None
        self.return_value = True

    def check_method(self):
        "description"
        if self.exception:
            raise self.exception
        return self.return_value

    def test_initialisation(self):
        check = Check("check_name", self.check_method)

        self.assertEquals(check.name, "check_name")
        self.assertEquals(check.description, "description")

    def test_initialisation_when_doc_is_none(self):
        def method():
            pass

        check = Check("check_name", method)

        self.assertEquals(check.description, "")

    def test_check_when_check_method_returns_true(self):
        check = Check("check_name", self.check_method)
        check.check()

        self.assertTrue(check.passed)

    def test_check_when_check_method_returns_false(self):
        self.return_value = False
        check = Check("check_name", self.check_method)
        check.check()

        self.assertFalse(check.passed)

    def test_check_when_check_method_raises_an_exception(self):
        self.exception = Exception("error")
        check = Check("check_name", self.check_method)
        check.check()

        self.assertFalse(check.passed)

    def test_check_returns_right_return_value(self):
        check = Check("check_name", self.check_method)

        self.assertEquals(check.check(), check.passed)

    def test_check_after_exception_has_exception_attribute(self):
        self.exception = Exception("error")
        check = Check("check_name", self.check_method)
        check.check()

        self.assertTrue("error" in check.exception)


class DummyPreflight(Preflight):

    fail = True

    def should_fail(self):
        return self.fail

    def check_success(self):
        return True

    def check_check_test(self):
        return True

    def check_maybe_fail(self):
        return not self.should_fail()


class ApplicationTestCase(TestCase):

    def test_initialisation(self):
        app = Application(DummyPreflight)

        self.assertEqual(app.name, "preflight checks")
        self.assertEqual(len(app.checks), 3)

    def test_check_name_is_properly_handled(self):
        app = Application(DummyPreflight)

        self.assertEqual(set(c.name for c in app.checks),
                         set(['success', 'check_test', 'maybe_fail']))

    def test_check_sets_passed_to_false_if_at_least_one_of_check_fails(self):
        app = Application(DummyPreflight)

        self.assertFalse(app.passed)

    def test_check_sets_passed_to_true_if_all_checks_passed(self):
        DummyPreflight.fail = False

        app = Application(DummyPreflight)

        self.assertTrue(app.passed)

        DummyPreflight.fail = True


class AuthenticatePass(Preflight):

    def authenticate(self, request):
        return True


class AuthenticateFail(Preflight):

    def authenticate(self, request):
        return False


def clear_registry():
    while REGISTRY:
        REGISTRY.pop()


class AutenticateTestCase(TestCase):

    def test_passes_if_all_classes_authenticate_passes(self):
        clear_registry()
        REGISTRY.append(AuthenticatePass)
        REGISTRY.append(AuthenticatePass)

        self.assertTrue(authenticate(None))

    def test_fails_if_at_least_one_class_authenticate_fails(self):
        clear_registry()
        REGISTRY.append(AuthenticatePass)
        REGISTRY.append(AuthenticateFail)

        self.assertFalse(authenticate(None))

    class BasicAuthPreflight(Preflight):
        @allow_basic_auth
        def authenticate(self, request):
            return request.user.is_staff

    basic_preflight = BasicAuthPreflight()
    auth = 'x:y'.encode('base64')

    def request(self, **meta):
        return Mock(user=AnonymousUser(), META=meta)

    def test_no_basic_auth_fails(self):
        request = self.request()
        self.assertFalse(self.basic_preflight.authenticate(request))

    @patch('preflight.views.django_authenticate')
    def test_basic_auth_succeeds(self, mock_authenticate):
        mock_authenticate.return_value = User(is_staff=True)
        request = self.request(HTTP_AUTHORIZATION='Basic %s' % self.auth)
        self.assertTrue(self.basic_preflight.authenticate(request))
        mock_authenticate.assert_called_once_with(username='x', password='y')

    @patch('preflight.views.django_authenticate')
    def test_inactive_user_fails(self, mock_authenticate):
        mock_authenticate.return_value = User(is_staff=True, is_active=False)
        request = self.request(HTTP_AUTHORIZATION='Basic %s' % self.auth)
        self.assertFalse(self.basic_preflight.authenticate(request))
        mock_authenticate.assert_called_once_with(username='x', password='y')

    @patch('preflight.views.django_authenticate')
    def test_basic_auth_bad_account(self, mock_authenticate):
        mock_authenticate.return_value = None
        request = self.request(HTTP_AUTHORIZATION='Basic %s' % self.auth)
        self.assertFalse(self.basic_preflight.authenticate(request))
        mock_authenticate.assert_called_once_with(username='x', password='y')

    def test_basic_auth_malformed(self):
        request = self.request(HTTP_AUTHORIZATION='Basic xyz')
        self.assertFalse(self.basic_preflight.authenticate(request))
        request = self.request(HTTP_AUTHORIZATION='Other %s' % self.auth)
        self.assertFalse(self.basic_preflight.authenticate(request))


class GatherChecksTestCase(TestCase):

    def test(self):
        clear_registry()
        REGISTRY.append(AuthenticatePass)
        REGISTRY.append(AuthenticatePass)
        REGISTRY.append(AuthenticateFail)

        applications = gather_checks()

        self.assertEquals(len(applications), 3)


class ExtraVersionAsCallable(Preflight):

    def versions(self):
        return [{'name': 'spam', 'version': 'ni'}]


class ExtraVersionAsList(Preflight):

    versions = [{'name': 'eggs', 'version': 'peng'}]


class GatherVersions(TestCase):

    def test_default_versions(self):
        clear_registry()

        versions = gather_versions()

        self.assertEquals(len(versions), 4)
        for item in versions:
            self.assertTrue('name' in item and 'version' in item)

    def test_get_extra_version_information_from_checks_class_method(self):
        clear_registry()
        REGISTRY.append(ExtraVersionAsCallable)

        versions = gather_versions()

        self.assertEquals(len(versions), 5)
        self.assertEquals(versions[-1]['name'], 'spam')

    def test_get_extra_version_information_from_class_attribute(self):
        clear_registry()
        REGISTRY.append(ExtraVersionAsList)

        versions = gather_versions()

        self.assertEquals(len(versions), 5)
        self.assertEquals(versions[-1]['version'], 'peng')


class PreflightCommandTestCase(TestCase):

    @patch('sys.exit')
    @patch.object(DummyPreflight, 'fail', new=False)
    def test(self, mock_exit):
        clear_registry()
        try:
            sys.stdout = StringIO()
            REGISTRY.append(DummyPreflight)

            call_command('preflight')

            self.assertTrue('checks for applications' in sys.stdout.getvalue())
        finally:
            sys.stdout = sys.__stdout__


class OverviewView(TestCase):
    @patch('preflight.views.authenticate')
    def test_overview_when_not_authenticated(self, mock_authenticate):
        mock_authenticate.return_value = False

        response = self.client.get(reverse('preflight-overview'))

        self.assertEqual(response.status_code, 404)

    @patch('preflight.views.render_to_response')
    @patch('preflight.views.authenticate')
    def test_overview_html(self, mock_authenticate, mock_render_to_response):
        mock_authenticate.return_value = True
        mock_render_to_response.return_value = HttpResponse()

        self.client.get(reverse('preflight-overview'))

        mock_render_to_response.assert_called_once()
        context = mock_render_to_response.call_args[0][1]
        self.assertTrue(isinstance(context, RequestContext))

    @patch('preflight.views.authenticate')
    def test_overview_json(self, mock_authenticate):
        mock_authenticate.return_value = True

        response = self.client.get(
            reverse('preflight-overview'), HTTP_ACCEPT='application/json')

        self.assertEqual(response['Content-Type'], 'application/json')


class SettingsTestCase(TestCase):
    @patch('preflight.models.settings')
    def test_gather_settings_no_location(self, mock_settings):
        mock_settings._wrapped.FOO = 'bar'
        mock_settings.FOO = 'bar'
        mock_settings.PREFLIGHT_HIDDEN_SETTINGS = ''
        settings = gather_settings()
        expected = [{'name': 'FOO', 'value': 'bar', 'location': ''}]
        self.assertEqual(expected, settings)

    @patch('preflight.models.settings')
    def test_gather_settings_with_location(self, mock_settings):
        mock_settings._wrapped.FOO = 'bar'
        mock_settings.FOO = 'bar'
        mock_settings.PREFLIGHT_HIDDEN_SETTINGS = ''
        parser = Mock()
        parser.locate.return_value = '/tmp/baz'
        mock_settings.__CONFIGGLUE_PARSER__ = parser
        settings = gather_settings()
        expected = [{'name': 'FOO', 'value': 'bar', 'location': '/tmp/baz'}]
        self.assertEqual(expected, settings)

    @patch('preflight.models.settings')
    def test_gather_settings_hidden(self, mock_settings):
        mock_settings._wrapped.FOO_ZOGGLES = 'bar'
        mock_settings.FOO_ZOGGLES = 'bar'
        mock_settings.PREFLIGHT_HIDDEN_SETTINGS = 'ZOGGLES'
        settings = gather_settings()
        expected = [{'name': 'FOO_ZOGGLES', 'value': '*' * 18, 'location': ''}]
        self.assertEqual(expected, settings)

    @patch('preflight.models.settings')
    def test_gather_settings_omitted(self, mock_settings):
        mock_settings._wrapped._FOO = 'bar'
        mock_settings._FOO = 'bar'
        mock_settings.PREFLIGHT_HIDDEN_SETTINGS = ''
        settings = gather_settings()
        self.assertEqual([], settings)


@skipIf(not settings.USE_GARGOYLE, 'skipping for Django 1.1')
class GargoyleTestCase(TestCase):

    def setUp(self):
        from gargoyle import gargoyle
        self.gargoyle = gargoyle
        from gargoyle.builtins import IPAddressConditionSet
        self.IPAddressConditionSet = IPAddressConditionSet
        from gargoyle.models import (
            Switch,
            DISABLED,
            SELECTIVE,
            GLOBAL,
            INHERIT
        )
        self.Switch = Switch
        self.DISABLED = DISABLED
        self.SELECTIVE = SELECTIVE
        self.GLOBAL = GLOBAL
        self.INHERIT = INHERIT
        self.gargoyle.register(self.IPAddressConditionSet())
        super(GargoyleTestCase, self).setUp()

    def get_switches(self):
        switches = [
            self.Switch(key='DISABLED', status=self.DISABLED,
                description='switch 1'),
            self.Switch(key='SELECTIVE_1', status=self.SELECTIVE),
            self.Switch(key='SELECTIVE_2', status=self.SELECTIVE),
            self.Switch(key='GLOBAL', status=self.GLOBAL),
            self.Switch(key='INHERIT', status=self.INHERIT),
        ]
        selective = switches[2]
        selective.add_condition(
            self.gargoyle,
            condition_set='gargoyle.builtins.IPAddressConditionSet',
            field_name='ip_address',
            condition='127.0.0.1',
        )
        return switches

    @patch.dict(sys.modules, **{'gargoyle': None})
    def test_gather_switches_no_gargoyle(self):
        self.assertEqual(gather_gargoyle(), None)

    def assert_switches_dict(self, actual):
        expected = [
            dict(name='DISABLED',
                 status=self.DISABLED,
                 description='switch 1',
                 status_text=self.Switch.STATUS_LABELS[self.DISABLED],
                 conditions=[]),
            dict(name='SELECTIVE_1',
                 status=self.SELECTIVE,
                 description=None,
                 status_text=self.Switch.STATUS_LABELS[self.GLOBAL],
                 conditions=[]),
            dict(name='SELECTIVE_2', status=self.SELECTIVE,
                 description=None,
                 status_text=self.Switch.STATUS_LABELS[self.SELECTIVE],
                 conditions=['IP Address(ip_address=127.0.0.1)']),
            dict(name='GLOBAL', status=self.GLOBAL,
                 description=None,
                 status_text=self.Switch.STATUS_LABELS[self.GLOBAL],
                 conditions=[]),
            dict(name='INHERIT', status=self.INHERIT,
                 description=None,
                 status_text=self.Switch.STATUS_LABELS[self.INHERIT],
                 conditions=[]),
        ]
        self.assertEqual(actual, expected)

    @patch('gargoyle.models.Switch.objects.all')
    def test_gather_switches(self, mock_all):
        mock_all.return_value = self.get_switches()
        self.assert_switches_dict(gather_gargoyle())

    @patch('gargoyle.models.Switch.objects.all')
    def test_gargoyle_template(self, mock_all):
        switches = self.get_switches()
        mock_all.return_value = switches
        the_switches = gather_switches()
        context = {
            "switches": the_switches,
            "preflight_base_template": BASE_TEMPLATE,
            "preflight_table_class": TABLE_CLASS,
        }
        response = render_to_string('preflight/overview.html', context)
        dom = PyQuery(response)
        table = dom.find('#switches-table tbody')
        self.assertEqual(table.find('tr')[0][0].text, 'gargoyle')

        for row, switch in zip(table.find('tr.switch'), switches):
            self.assertEqual(row[0].text, switch.key)
            self.assertEqual(row[1].text, str(switch.description))
            self.assertEqual(row[3].text, switch.get_status_label())
