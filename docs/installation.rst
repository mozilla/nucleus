.. installation:

==========================================
Installing a Local Development Environment
==========================================

.. note::

    Installing Nucleus might be daunting.  Ask for help in
    #nucleus on irc.mozilla.org.

**Prerequisites:** You 'll need python 2.6, virtualenv and pip.  You'll also need
mysql-dev (or the equivalent on your system), and MySQL server.

You will probably also want a \*nix box; Nucleus has never been installed on Windows.

Step-by-Step Guide
------------------

When you want to start contributing...

#. Fork `the main Nucleus repository on Github <https://github.com/mozilla/nucleus>`_.

#. Clone your fork to your local machine::

    $ git clone --recursive git@github.com:YOUR_USERNAME/nucleus.git nucleus
    (lots of output - be patient...)
    $ cd nucleus

   .. note::

    Make sure you use ``--recursive`` when checking the repo out! If you
    didn't, you can load all the submodules with ``git submodule update --init
    --recursive``.

#. Create your python virtual environment::

    $ virtualenv venv

#. Activate your python virtual environment::

    $ source venv/bin/activate
    (venv) $

   .. note::

    When you activate your python virtual environment, 'venv'
    (virtual environment's root directory name) will be prepended
    to your PS1.

#. Install development and compiled requirements::

    (venv)$ pip install -r requirements/compiled.txt -r requirements/dev.txt
    (lots more output - be patient again...)
    (venv) $

   .. note::

    Since you are using a virtual environment, all the python
    packages you will install while the environment is active
    will be available only within this environment. Your system's
    python libraries will remain intact.

#. Configure your local nucleus installation::

        (venv)$ cp nucleus/settings/local.py-dist nucleus/settings/local.py

   * Set BROWSERID_AUDIENCES to your local IP and port (below, 127.0.0.1:8000)
   * Set SESSION_COOKIE_SECURE to False (unless you're using https locally)
   * Set a SECRET_KEY
   * Set an HMAC_KEY
   * Provide a username, database name, hostname and password for MySQL

    .. note::

        The provided configuration uses a MySQL database named `nucleus` and
        accesses it locally using the user `root` with no password.  You can see
        :doc:`mysql` if you need help creating a user and database.

#. Sync DB and apply migrations::

    (venv)$ ./manage.py syncdb --noinput --migrate

#. Create user using `the Django shell <https://docs.djangoproject.com/en/1.5/ref/django-admin/#shell>`_::
    
    (venv)$ python manage.py shell

    Type "help", "copyright", "credits" or "license" for more information.
    (InteractiveConsole)

    >>> from django.contrib.auth.models import User
    >>> User.objects.create(
        username='you@example.com',
        email='you@example.com',
        password='!',
        is_staff=True,
        is_superuser=True,
        is_active=True
    )

#. Run server::

    (venv)$ ./manage.py runserver 127.0.0.1:8000

#. Load http://127.0.0.1:8000/admin in your browser and sign in with Persona. You're in!

#. When finished working on Nucleus, deactivate your virtual python environment by running::

     (venv)$ deactivate
     $

#. Next time:

   Next time, before starting you will need to activate your environment by typing::

     $ . $VIRTUAL_ENV/bin/activate

Have fun!

See Also
--------

.. toctree::
    :maxdepth: 2

    mysql
