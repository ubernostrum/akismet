.. _test-clients:

.. currentmodule:: akismet


The test clients
================

Two special classes are provided which you can use to test your use of Akismet without
needing to make real requests to the Akismet web service, and also without needing to
build and maintain a set of test mocks to replace the real Akismet clients. Both of
these clients are configured by subclassing them and setting attributes to specify the
desired behavior.

For examples of using these test clients, including a pytest plugin for easy access to
test clients, see :ref:`the testing section of the usage guide <usage-testing>`.

.. autoclass:: TestAsyncClient
.. autoclass:: TestSyncClient
