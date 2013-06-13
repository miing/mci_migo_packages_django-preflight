Api Usage
=========


JSON Access
-----------

If you request the preflight page with an "Accept: application/json" header,
preflight will return the various settings, applications, versions and switches
data in JSON form.

This can be useful in CI automation environments, where integrations tests may
need to inspect how a service is configured in order to run the correct tests,
for example.

Authentication
--------------

When accessing the json api from a script, authentication can be tricky. Cookie
based authentication is harder from a script, and things like OpenID login even
more so.

So simplify this, preflight includes an @allow_basic_auth decorator (in
preflight.models). This decorator can be used to allow limited HTTP basic auth
access to preflight by decorating your authenticate() method with it. If the
user is not authenticated, it will check for basic auth credentials, and
validate them using the standard django authentication backend. If valid, it
will set request.user as approriate. The user is *not* logged in.  WARNING:
only use in production if you are using HTTPS.
