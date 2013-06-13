# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from django.conf.urls.defaults import (
    handler404, handler500, include, patterns
)

import preflight


preflight.autodiscover()

urlpatterns = patterns('',
    (r'^preflight/', include('preflight.urls')),
)
