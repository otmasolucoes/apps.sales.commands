===================
Otma Sales Commands
===================

Module for commands in company projects django.
Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "otma.apps.sales.commands" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'otma.apps.sales.commands',
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('sales/commands/', include('otma.apps.sales.commands.urls')),

3. Run `python manage.py migrate` to create the commands models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to verify core models (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/sales/ to participate in the poll.