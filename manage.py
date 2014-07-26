#!/usr/bin/env python
import os
import sys

def init_for_puinstaller():
    # For django 1.6 hack
    from django.core import management
    management.get_commands()
    management._commands.update({
     'check': 'django.core',
     'createcachetable': 'django.core',
     'diffsettings': 'django.core',
     'dumpdata': 'django.core',
     'findstatic': 'django.contrib.staticfiles',
     'flush': 'django.core',
     'inspectdb': 'django.core',
     'loaddata': 'django.core',
     'makemessages': 'django.core',
     'sql': 'django.core',
     'sqlall': 'django.core',
     'sqlclear': 'django.core',
     'sqlcustom': 'django.core',
     'sqldropindexes': 'django.core',
     'sqlflush': 'django.core',
     'sqlindexes': 'django.core',
     'sqlinitialdata': 'django.core',
     'sqlsequencereset': 'django.core',
     'startapp': 'django.core',
     'startproject': 'django.core',
     'syncdb': 'django.core',
     'test': 'django.core',
     'testserver': 'django.core',
     'validate': 'django.core',
     'vendor': 'thief.vendors'})

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "thief.settings")
    init_for_puinstaller()
    from django.core.management import execute_from_command_line
	
    execute_from_command_line(sys.argv)
