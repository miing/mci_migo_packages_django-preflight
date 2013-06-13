Versions
========

Version's List
--------------

Besides checks django-preflight provides a list of versions for
various components. That information is only accessible via web
interface, because it's very easy to get that information from the
command line.

Naturally you have an ability to extend this information with any
other component you like. By default it contains versions of: Python,
Django and django-preflight itself.


Extending Versions List
-----------------------

As with other things, main extension point is ``Preflight`` class. You
can either add ``versions(self)`` method, which should return list of
dictionaries, each one containing ``name`` and ``version`` keys or add
class attribute called ``versions`` containing the same information.

The method version can be useful if you want to check some items
dynamically or include them only if they are available and skipping
them otherwise.


Method Example
--------------

An example where ``versions`` is a method:

.. testcode::

    import preflight

    class AppPreflight(preflight.Preflight):
        def versions(self):
            try:
                import simplejson
                return [{'name': "simplejson", 
                         'version': simplejson.__version__}]
            except ImportError:
                return []

    preflight.register(AppPreflight)

.. testoutput::
   :hide:

In this case, if simplejson is available its version will be added to
the list of packages displayed by django-preflight.


Attribute Example
-----------------

An example where ``versions`` is an iterable:

.. testcode::

    import preflight
    import setuptools
    
    class AppPreflight(preflight.Preflight):
 
        versions = [
            {'name': "setuptools", 'version': setuptools.__version__}
        ]

    preflight.register(AppPreflight)

.. testoutput::
   :hide:

On the other hand, this example causes the app to require
``setuptools`` to be installed and will fail if this is not the case.
