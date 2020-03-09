# Otma Core

Core for company projects. To install app:

	1. Execute: pip install https://github.com/otmasolucoes/apps.sales.commands/zipball/master

	2. Add "apps.entities" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'otma.apps.sales.commands',
    ]

	3. Include the polls URLconf in your project urls.py like this:

    	path('entities/', include('otma.apps.sales.commands.urls')),

	4. Run `python manage.py migrate` to create the core models.