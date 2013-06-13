Configuration
=============

You can customize django-preflight's behaviour in several
ways. Easiest one is to use configuration options.


``settings.py``
---------------

``PREFLIGHT_BASE_TEMPLATE`` Name of the base template which will be
  extended by preflight's page. It should contain ``title`` and
  ``content`` blocks.

  Default: ``index.1col.html``

``PREFLIGHT_TABLE_CLASS``
  A name of the CSS class which will be applied to the tables on the
  overview page.

  Default: ``listing``


Other customizations
--------------------

Other ways in which you can customize django-preflight are tightly
coupled with creating checks and are discussed in the next section.
