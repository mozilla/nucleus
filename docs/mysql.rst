.. mysql:

===========
MySQL setup
===========

Setting up a MySQL user and database for development:

#. Install the MySQL server. Many Linux distributions provide an installable
   package. If your OS does not, you can find downloadable install packages
   on the `MySQL site`_.

.. _MySQL site: http://dev.mysql.com/downloads/mysql/

#. Start the mysql client program as the mysql root user::

    $ mysql -u root -p
    Enter password: ........
    mysql>

#. Create a ``nucleus`` user::

    mysql> create user 'nucleus'@'localhost';

#. Create a ``nucleus`` database::

    mysql> create database nucleus;

#. Give the nucleus user access to the nucleus database::

    mysql> GRANT ALL PRIVILEGES ON nucleus.* TO "nucleus"@"localhost";
    mysql> EXIT
    Bye
    $
