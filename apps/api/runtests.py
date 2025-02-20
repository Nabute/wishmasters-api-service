import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
import coverage

if __name__ == '__main__':
    # Set up Django settings module environment variable
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_service.test_settings')

    # Set up Django
    django.setup()

    # Initialize coverage and specify source tracking
    cov = coverage.Coverage(
        source=[app for app in settings.INTERNAL_APPS]
    )
    cov.start()

    # Get test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    # Run tests for all installed apps
    failures = test_runner.run_tests(settings.INTERNAL_APPS)

    # Stop coverage and save report
    cov.stop()
    cov.save()

    # Print coverage report
    print("\nCoverage Report:")
    cov.report(show_missing=True)

    # Exit with appropriate status code
    sys.exit(bool(failures))
