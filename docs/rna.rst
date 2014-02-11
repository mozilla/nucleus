===
RNA
===

Overview
--------

RNA is the Release Notes publishing application. It is installed in both
Nucleus and Bedrock. 

In RNA, Release Managers input information about a particular release 
(using the administrative interface on nucleus.mozilla.org). That information
is immediately available through the `RNA API 
<https://nucleus.mozilla.org/rna/>`_. Bedrock queries this API periodically
and refreshes its own internal database cache of release notes.

When a request for a release notes page hits Bedrock, Bedrock responds with...

* A cached copy of that page (if cache exists) or
* A page rendered from a local copy of RNA data using a Bedrock template 
  (if no cache exists)

Creating a New Release
----------------------

To come.

Using the RNA API
-----------------

To come.
