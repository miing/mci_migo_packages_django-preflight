import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'preflight_example_project.settings'
sys.path.insert(0, 'preflight_example_project')

try:
    from django.test.utils import get_runner
except ImportError:
    from django.test.simple import run_tests
    get_runner = lambda s: run_tests

from django.conf import settings



def tests():
    TestRunner = get_runner(settings)
    if hasattr(TestRunner, 'func_name'):
        # Before change in Django 1.2
        failures = TestRunner(['preflight'])
    else:
        test_runner = TestRunner()
        failures = test_runner.run_tests(['preflight'])

    sys.exit(bool(failures))



if __name__ == '__main__':
    tests()
