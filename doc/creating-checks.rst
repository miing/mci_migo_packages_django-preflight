Creating checks
===============

Conventions
-----------

There are four steps to create a check:

 1. Create ``preflight.py`` file in your application's directory.
 2. In that file create a class which inherits from
    ``preflight.Preflight``.
 3. Add a method to that class with name starting with ``check_``.
 4. Register that class by calling ``preflight.register(ClassName)``

Those check methods are used by web interface and by command line
one. You can see the results of them being run by either accessing the
preflight page or by running ``$ ./manage.py preflight`` command.


Check's description
-------------------

The docstring of the method is displayed on the web page as a
description of the check. You can use it to document what it is
checking and what to do in case it fails. Ideally, one should check
only one thing, so reason of the failure would be obvious.


Success or Failure
------------------

To the check to be considered successful it needs to return a
``True``. Returning ``False`` or raising an exception means that the
check have failed. The system records the results from all the checks
from all of the applications and presents it to the end user.


An Example
----------

Below is an example of simple preflight class which checks if cache is
accessible from Django's process:

.. testcode::

    # this line is required for Python versions < 
    from __future__ import absolute_import
    
    import preflight


    class AppPreflight(preflight.Preflight):

        def check_cache_is_accessible(self):
            """
            Try to access cache, if it fails that means the caching
            is not properly configured or the cache server is down.
            """
            from django.core.cache import cache
            cache.set('test', 'value')
            if cache.get('test') == 'value':
                cache.delete('test')
                return True
            else:
                return False

    preflight.register(AppPreflight)
    
.. testoutput::
   :hide:

If everything is properly configured this check method will return
``True``, which means that it succeeded.

But if something is wrong, like, for example, missing python-memcached
library, the exception will be raised and will cause this check to
fail.

Third option is when this check returns ``False``, which means
that the cache is accessible, but is not storing proper values. Not a
good sign either.

.. note:: I'm aware this check can fail for more than one reason. It
          would be possible to split it into two smaller checks, but
          that would only made this example more complicated.
