# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from datetime import datetime
import json
import functools

from django.contrib.auth import authenticate as django_authenticate
from django.views.decorators.cache import never_cache
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from .models import (
    authenticate,
    gather_checks,
    gather_settings,
    gather_versions,
    gather_switches,
)
from .conf import BASE_TEMPLATE, TABLE_CLASS


JSON_TYPE = 'application/json'


@never_cache
def overview(request):
    if not authenticate(request):
        raise Http404

    data = {
        "applications": gather_checks(),
        "versions": gather_versions(),
        "settings": gather_settings(),
        "switches": gather_switches(),
    }
    # poor man's conneg
    if JSON_TYPE in request.META.get('HTTP_ACCEPT', ''):
        return HttpResponse(json.dumps(data), content_type=JSON_TYPE)
    else:
        data.update(
            preflight_base_template=BASE_TEMPLATE,
            preflight_table_class=TABLE_CLASS,
            now=datetime.now(),
        )
        return render_to_response(
            "preflight/overview.html", RequestContext(request, data))


def check_basic_auth(request):
    try:
        authentication = request.META.get('HTTP_AUTHORIZATION', None)
        if authentication:
            auth_method, auth = authentication.split(' ', 1)
            if auth_method.lower() == 'basic':
                auth = auth.strip().decode('base64')
                username, password = auth.split(':')
                user = django_authenticate(
                    username=username, password=password)
                if user is not None and user.is_active:
                    return user
    except Exception:
        # basic auth failed for some reason
        pass

    return None


def allow_basic_auth(f):
    @functools.wraps(f)
    def wrapper(self, request):
        if not request.user.is_authenticated():
            basic_user = check_basic_auth(request)
            if basic_user is not None:
                request.user = basic_user
        return f(self, request)
    return wrapper


