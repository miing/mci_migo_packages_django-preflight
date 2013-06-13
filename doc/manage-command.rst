Management Command
==================


Command
-------

Together with web page on which you can check the results of all your
checks django-preflight provides a Django management command. This
allows you to make sure that all is properly configured without the
need of going through the web server.

It can even be incorporated as a part of automatic health checks (or
other scripts), as it properly returns the exit codes. 0 if everything
is working and 1 otherwise.


Usage
-----

The invocation of the command is very simple. Once you have the app
installed just use::

    $ python manage.py preflight

which should return something similar to the following::

    Pre-flight checks for applications
    ====================================================
    
    app checks
    ----------------------------------------------------
    media_root_is_writable                          OK
    cache_is_usable                                 OK
    twitter_api_key_is_correct                      OK


of course, the exact result will highly depend on the exact checks,
project's structure and django-preflight configuration.

In case of any check failures the ``OK`` will be replaced with
``ERROR`` status.
