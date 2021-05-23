.. _about:

About
=====
A project for anyalzing warframe market data.

Versioning
----------

This package supports python 3.7.1 and up.

Credit
----------

All the data and information is credited to the creators of warframe.market. The public API is used to access warframe market data and process it.

Why?
----

Accesing warframe market is simple and easy task. However, it
is not currently easy to anyalze the price trends on warframe market
to a greater extent than the relatively simple statiscis page. This library
intends to give some basic tools to provide perform this anyalsis. For example,
this library can rank prime items in order to sell based on previous data::

    >>> from warframe_metrics.market.prime import prime_ranking
    >>> prime_ranking(vault_csv, prime_data, buy=True)
