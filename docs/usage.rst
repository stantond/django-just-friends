=====
Usage
=====


Installation
============

* Install with pip::

    pip install django-just-friends

* Add ``friendship`` to ``INSTALLED_APPS``
* Run ``migrate``::

    manage.py migrate

* Add to your project urls.py:

    url('', include('friendship.urls', namespace="friendship")),


Getting data in a view:

    --------------------------------------
    # Required Imports
    --------------------------------------

        from friendship.models import Friend

    --------------------------------------
    # Friends
    --------------------------------------

        # List of the current user's friends as User objects
        all_friends = Friend.objects.friends(user)

        # Count of the current user's friends
        friend_count = Friend.objects.friend_count(user)

        # Bool, True if two users are friends
        is_friend = Friend.objects.are_friends(user1, user2):

    --------------------------------------
    # Friendship Requests
    --------------------------------------

        # List of all received friendship requests
        requests_received = Friend.objects.received_requests(user)

        # List of all pending recieved friendship requests (all that have not been rejected)
        requests_received = Friend.objects.pending_received_requests(user)

        # Count of all pending recieved friendship requests  (all that have not been rejected)
        count = Friend.objects.pending_received_request_count(user)

        # List of all unread recieved friendship requests
        requests_received = Friend.objects.unread_received_requests(user)

        # Count of all unread recieved friendship requests
        requests_received = Friend.objects.unread_received_request_count(user)

        # List of all read recieved friendship requests
        requests_received = Friend.objects.read_received_requests(user)

        # List of all rejected recieved friendship requests
        requests_received = Friend.objects.rejected_received_requests(user)

        # List of all sent friendship requests
        requests_sent = Friend.objects.sent_requests(user)

        # Bool, True if FriendshipRequest sent from user1 to user2
        have_sent = Friend.objects.have_sent_request(user1, user2)

        # Bool, True if FriendshipRequest received by user1 from user2
        have_received = Friend.objects.have_received_request(user1, user2)

        # Bool, True if FriendshipRequest exists between user1 and user2 (in either direction)
        exists = Friend.objects.request_exists_between(user1, user2)

Managing Friendships:

    --------------------------------------
    # Using the django-just-friends views
    --------------------------------------

        The django-just-friends views are designed to be called from within a template,
        processing the friendship then immediately redirecting the user back to the previous page. N.B. `mark_as_viewed()` must still be called manually, as this depends on the behaviour you want, e.g. get unread requests in a view, run mark_as_viewed on them, show them as 'new'. The next time the user loads the page, they will not be new.

        # Make a new friendship request / Create a new FriendshipRequest
        <a href="{% url 'friendship:request' user2.username %}?from={{ request.path|urlencode }}">Add friend</a>

        # Cancel a pending friendship request / Delete a Friendship Request
        <a href="{% url 'friendship:cancel' friendship_request.id %}?from={{ request.path|urlencode }}">Cancel Request/a>

        # Accept a friendship request / Create a new Friend and delete the corresponding FriendshipRequest
        <a href="{% url 'friendship:accept' friendship_request.id %}?from={{ request.path|urlencode }}">Accept Request</a>

        # Reject a friendship request / Set FriendshipRequest.reject to timezone.now()
        <a href="{% url 'friendship:reject' friendship_request.id %}?from={{ request.path|urlencode }}">Reject Request</a>

        # Unfriend / Delete a Friend
        <a href="{% url 'friendship:unfriend' user2.username %}?from={{ request.path|urlencode }}">Unfriend</a>


    --------------------------------------
    # Manual Management
    --------------------------------------

        # Make a new friendship request / Create a new FriendshipRequest
        # A message (string) can be passed as an optional third parameter
        try:
            Friend.objects.add_friendship_request(request.user, to_user)
        except AlreadyExistsError as e:
            context = {'errors': ["%s" % e]}

        # Cancel a pending friendship request / Delete a Friendship Request
        f_request = get_object_or_404(request.user.friendship_requests_received, id=friendship_request_id)
        f_request.cancel()

        # Accept a friendship request / Create a new Friend and delete the corresponding FriendshipRequest
        f_request = get_object_or_404(request.user.friendship_requests_received, id=friendship_request_id)
        f_request.accept()

        # Reject a friendship request / Set FriendshipRequest.reject to timezone.now()
        f_request = get_object_or_404(request.user.friendship_requests_received, id=friendship_request_id)
        f_request.reject()

        # Mark a request as viewed / Set FriendshipRequest.reject to timezone.now()
        f_request = get_object_or_404(request.user.friendship_requests_received, id=friendship_request_id)
        f_request = mark_viewed()

        # Unfriend / Delete a Friend
        Friend.objects.unfriend(request.user, to_user)

Errors:

        # Attempting to create an already existing friendship will raise
        # `friendship.exceptions.AlreadyExistsError`, a subclass of
        # `django.db.IntegrityError`.