.. Eaterator Web documentation master file, created by
   sphinx-quickstart on Thu Mar  9 21:23:28 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Eaterator Web's documentation!
=========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   authentication
   users
   recipes
   admin

Required Headers
================
API calls (except for authentication) require the following headers:

.. code-block:: none

	"Authorization" => "Bearer ccccccc.ccccccccccc.cccccccc"
	"Content-Type"  => "application/json"

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
