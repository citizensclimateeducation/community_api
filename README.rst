swc_api
=======

swc_api contains classes and utilities for interacting with the Small World Community REST API.

``swc_connection()`` returns a request Session object configured to implement JWT refreshing, paging, and throttling.

The ``CommunityToken`` class handles fetching JWT tokens for interacting with Community.

Installation
------------

To install locally: 

Checkout the project from Github::

    > git clone https://github.com/citizensclimateeducation/community_api.git

Then (with the virtual environment active for the project you'll be using this with)::

    > pip install -e /path/to/community_api

To install via pypi::

    > pip install swc-api

Documentation
-------------

To create a session based on environmental variables, create a ``.env`` file with the following variables set based on your Community instance::

    export SWC_AUDIENCE=[community.yourdomain.org]
    export SWC_APP_ID=[Application ID for your OAuth Application]
    export SWC_USER_ID=[Authorized User for your OAuth Application]
    export SWC_SECRET=[OAuth secret for your Oauth Application]

Source the ``.env`` file before running your application and you won't need to set these variables when instantiating the
api client::

    > from swc_api import swc_connection
    > swc = swc_connection()
    > # make calls to the API endpoint
    > group_members = swc.get_all("groups/[groupId]/members", params={"embed": "user"})

However you can pass these variables in manually as well::

    from swc_api import swc_connection, CommunityToken
    swc = swc_connection(
        community_domain="[your domain]",
        app_id="[OAuth App ID]",
        user_id=[Authorized User Id],
        app_secret="OAuth App Secret",
    )
    group_members = swc.get_all("groups/[groupId]/members", params={"embed": "user"})

Usage and pagination
~~~~~~~~~~~~~~~~~~~~

You can make regular ``requests`` calls with the ``swc_connection`` and will receive a standard ``Response`` object back.

The session also has a ``get_all`` method which will handle pagination for result sets longer than 500 objects. The
``get_all`` method will return a JSON response rather than a ``requests.models.Response`` object.

An example of an update would be::

  swc.post("groups/[id]/members", json={"userId": "[userId]"})
  # response
  {
    'id': '[membershipId]',
     'groupId': '[groupId]',
     'userId': '[userId]',
     'status': '1',
     'joinDate': '2020-07-20T12:43:07-07:00',
     'invited': True
  }

Notes and Considerations
------------------------

Currently throttling and error handling is very basic. After each response is returned the session sleeps for the
duration indicated by ``SWC_API_RATE``. This means that the duration of the call is not taken into consideration, nor are
calls made in other threads. There are also no intelligent retry mechanisms built in.

Given those limitations, this should probably not be used for front-facing production applications, but for other
purposes such as analyzing data, looking at fields provided in the API but not Community Reports or making bulk updates
not available in the Community Admin Import Manager.
