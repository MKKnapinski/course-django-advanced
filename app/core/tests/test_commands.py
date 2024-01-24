"""
Test custom Django management commands.
"""

from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands"""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database ready."""
        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    # the order or patched arguments is important
    # it applies the arguments from the inside out
    # first we've got self, which is always the first
    # then patched_sleep because we mock method on method level
    # then patched_check because it's mocked at class level
    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError."""
        # the first 2 times we call the method we want to raise a Psycopg2Error
        # \ breaks into multiple lines
        # next 3 times we raise OperationalError
        # finally we get True back. It's not an exception, so it knows to return it
        patched_check.side_effect = [Psycopg2Error] * 2 + \
                                    [OperationalError] * 3 + \
                                    [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
