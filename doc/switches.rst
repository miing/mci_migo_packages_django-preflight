
Switches
========

Switches Table
--------------

Django-preflight has optional integration with the gargoyle feature flag app,
which provides run-time dynamic feature switches. If you have gargoyle
installed, and it's in your settings.INSTALLED_APPS, and you're on django 1.2
or greater, then preflight will display a table with current switch settings
in.

Preflight only supports gargoyle currently, but support for other feature flag
apps is possible.

