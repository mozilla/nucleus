=====================
Understanding Nucleus
=====================

Nucleus Architecture
--------------------

Nucleus is designed to enable dynamic publishing of content on 
`www.mozilla.org <https://www.mozilla.org>`_. It is deliberately designed
to run as a standalone instance of Django rather than inside `Bedrock 
<http://bedrock.readthedocs.org>`_, the Playdoh application that serves
www.mozilla.org's content. This design...

* Keeps Bedrock's database very secure by limiting the number of users
  who can sign in as site administrators.
* Keeps the Bedrock application very lean and focused on serving web pages, 
  rather than supporting numerous unique publishing workflows.
* Minimizes the amount of change on Bedrock, decreasing the risk of downtime.
* Allows Bedrock and Nucleus to meet different uptime expectations (Nucleus
  does not require the same service level as Bedrock does).
* Provides public content in a public API, which creates the possibility of
  additional applications for the data or republication on other sites.
* Allows either Bedrock or Nucleus to be replaced or refactored 
  independently of the other.

Nucleus is a Django project. Every distinct publishing workflow in Nucleus
(for example, Release Notes or Security Bulletins) is built as a 
`Django application <https://docs.djangoproject.com/en/dev/ref/applications/#projects-and-applications>`_. These applications can have their own data models,
authorization rules, and interfaces. 

Some Nucleus applications will be installed both in Nucleus and in Bedrock. 
This allows Bedrock to cache application data in Bedrock's database, adding
an additional layer of redundancy and reducing rendering latency.

Nucleus is deployed on Mozilla's PaaS infrastructure. For more information
about the PaaS, see `the PaaS mailing list 
<https://mail.mozilla.org/listinfo/paas-users>`_.

List of Publishing Workflows
----------------------------

.. toctree::
    :maxdepth: 2

    rna 

