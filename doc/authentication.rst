Authentication
==============


Defaults
--------

Due to high sensitivity of the information provided on preflight page
it's highly advisable to limit access to it.

By default only registered users which have access to Django admin can
see that page and all the rest will get a 404 error page.


Customization
-------------

But if this is not enough or if you need some other way of assesing
the access right you can provide your own code.

Each preflight class can have an ``authenticate(self, request)``
method which gets a request object and returns ``True`` if given
request is authorized to access that page. Otherwise the 404 error
code will be returned.


Multiple preflight files
------------------------

As you may have noticed, the ``authenticate`` method is supplied for
each application and not for whole project. This brings the question
what would happen if two or more applications contain ``authenticate``
method?

In that case, given request must have be approved by all the
``authentication`` methods before the page is displayed. It's enough
for just one to veto the access. This means, that you can only tighten
up the security when adding new preflight classes, never loosen it up.


Example
-------

Below is quick example of implementing very simple way of
authorization schema. This particular one only allows one user to
access this page:

.. testcode::

    import preflight

    class AppPreflight(preflight.Preflight):
    
        def authenticate(self, request):
            if request.user.username == 'blackknight':
                return True

    preflight.register(AppPreflight)

.. testoutput::
   :hide:
