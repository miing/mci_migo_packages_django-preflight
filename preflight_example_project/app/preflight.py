# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from __future__ import absolute_import

from django.conf import settings

import os.path
import preflight
import tempfile


class AppPreflight(preflight.Preflight):

    def authenticate(self, request):
        # Allow everybody to access this page. Default implementation restricts
        # this to people who can access /admin/ pages (user.is_stuff == True).
        return True

    def versions(self):
        return [{'name': 'foo-bar', 'version': '1.2.3'}]

    def check_media_root_is_writable(self):
        """Check if current MEDIA_ROOT directory is writable."""
        path = os.path.realpath(settings.MEDIA_ROOT)

        # Try writing to temporary file in MEDIA_ROOT
        tmp = tempfile.TemporaryFile(dir=path)
        tmp.write("test")
        tmp.close()

        # If we reached this point this means the directory itself is
        # writable. In case of any errors an exception would cause the check to
        # fail. Return value informs preflight that everything went right.
        return True


preflight.register(AppPreflight)
