Install django-preflight
========================

Install the code
----------------

django-preflight is just a regular Django application and only
requirement for it to be usable is to be importable by Django
project. That means you can put it directly into your project's
directory and it will work just find. Alternatively you can install it
using common python tools::

    $ pip install django-preflight

or::

    $ easy_install django-preflight

Or even download the source code and run::

    $ python setup.py install

from the source code directory.


Update ``settings.py``
----------------------

Once the code is installed you need to setup your Django's project
properly. First thing is to include it in ``INSTALLED_APPS`` list::

    # settings.py
    INSTALLED_APPS = (
        ...
        'preflight',
        ...
    )

django-preflight by itself doesn't have any extra dependecies.

Because this project doesn't include any models, there's no need of
updating your database schema.


Update ``urls.py``
------------------

Last bit of configuration is to run preflight discovery code and to
include it somewhere in the url's definition. The easiest way for
doing both of those steps is to modify project's ``urls.py`` file. It
should look like the following:

.. testcode::

    from django.conf.urls import *

    import preflight
    import preflight.urls


    preflight.autodiscover()

    urlpatterns = patterns('',
        (r'^preflight/', include(preflight.urls)),
    )

.. testoutput::
   :hide:

Two things here. Line with ``include(preflight.urls)`` sets the URL on
which the preflight page will be accessible. You can make this
anything you want, here it's set to ``/preflight/``.

Second is ``preflight.autodiscover()`` call which triggers search for
``preflight.py`` modules in all installed applications. Similar to
Django's admin ``admin.autodiscover()`` call.  This enables you to
just drop such file into your application folder.


Compatibility
-------------

django-preflight is compatible with released Django versions since
1.1, up to current 1.5. To be sure about this it's tested using tox_
against all of them.

Additionally it's tested on Python 2.6 and 2.7, all of that on `Ubuntu
Linux`_.

.. _tox: http://codespeak.net/tox/
   _Ubuntu Linux: http://www.ubuntu.com
