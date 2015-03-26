djenerics
=========

  A collection of Django 1.5+ and Django Rest Framework 3.0+ utilities


installation
------------

You can use pip to install the package::

    $ pip install djenerics


Then add it to the list of installed apps::

    INSTALLED_APPS = (
        'djenerics'
    )


model mixins
------------

The following mixins are available for your model classes:

Timestampable
    Provides `created_at` and `updated_at` fields.

Ownerable
    Provides a `owner` field which references `settings.AUTH_USER_MODEL`


view mixins
-----------

The following mixins are available for your view classes:

SelectRelatable
    Provides a class variable `select_related` that allows you to provide a
    tuple or list of related models to perform a select_related on.


django-rest-framework filter backend
------------------------------------

A custom filter backend that provides a generic filter query string parameter.

Convert a search query into a dictionary.

A search query like this one::

    party: stakker is akker category:"hiha hoi"

Will be converted to a python dict::

    {
        'category': 'hiha hoi',
        'party': None,
        'search': 'stakker is akker'
    }

It uses a regular expression to split every token on the `:`
separator instead of using the string.split() function. This is
important to distinguish between the following use cases::

    - 'party:'        => {'party': None}
    - 'party:tester'  => {'party': 'tester'}
    - 'party: tester' => {'search': 'party: tester'}


django-rest-framework serializer mixins
---------------------------------------

The following mixins are available for your serializer classes:

Projectable
    Gives your api consumers the ability to control what fields are included in
    the api response using a configurable query string parameter (defaults to
    `_fields`).

    E.g. a `GET /resources?_fields=name,description,count` will only return the
    specified 3 fields of the `resource`.

Ownerable
    Limit the related field options to only those records owned by the current
    logged in user.
