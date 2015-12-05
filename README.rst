# django-just-friends
A simple friends system for Django

Loosely based on [django-friendship by Frank Wiles](https://github.com/revsys/django-friendship/).

## Setting Up
 - Add `justfriends` to `INSTALLED_APPS` and run `manage.py migrate`.
 - Add `url('', include('justfriends.urls', namespace="justfriends")),` to your project urls.py

## Managing Friendships

#### Using the django-just-friends views
The django-just-friends views are designed to be called from within a template, processing the friendship then immediately redirecting the user back to the previous page. If you'd rather not use these views, see `Manual Management` below.

N.B. `mark_as_viewed()` must still be called manually, depending on when you consider a request to be 'read'.

**Request** a new friendship / Create a new FriendshipRequest

`<a href="{% url 'friendship:request' user2.username %}?from={{ request.path|urlencode }}">Add friend</a>`

**Cancel** a pending friendship request / Delete a Friendship Request

`<a href="{% url 'friendship:cancel' friendship_request.id %}?from={{ request.path|urlencode }}">Cancel Request/a>`

**Accept** a friendship request / Create a new Friend and delete the corresponding FriendshipRequest

`<a href="{% url 'friendship:accept' friendship_request.id %}?from={{ request.path|urlencode }}">Accept Request</a>`

**Reject** a friendship request / Delete the FriendshipRequest

`<a href="{% url 'friendship:reject' friendship_request.id %}?from={{ request.path|urlencode }}">Reject Request</a>`

**Unfriend** / Delete a Friend

`<a href="{% url 'friendship:unfriend' user2.username %}?from={{ request.path|urlencode }}">Unfriend</a>`

If you're calling from your site's homepage, use `from=/`

#### Manual Management

**Request** a new friendship / Create a new FriendshipRequest

*A message (string) can be passed as an optional third parameter*
```
try:
    Friend.objects.add_friendship_request(request.user, to_user)
except AlreadyExistsError as e:
    context = {'errors': ["%s" % e]}
```
**Cancel** a pending friendship request / Delete a Friendship Request
```
f_request = get_object_or_404(request.user.friendship_requests_received, id=friendship_request_id)
f_request.cancel()
```
**Accept** a friendship request / Create a new Friend and delete the corresponding FriendshipRequest
```
f_request = get_object_or_404(request.user.friendship_requests_received, id=friendship_request_id)
f_request.accept()
```
**Reject** a friendship request / Delete the FriendshipRequest
```
f_request = get_object_or_404(request.user.friendship_requests_received, id=friendship_request_id)
f_request.reject()
```
**Unfriend** / Delete a Friend
```
Friend.objects.unfriend(request.user, to_user)
```
**Mark as viewed** a **single request** / Set FriendshipRequest.viewed to timezone.now()
```
f_request = get_object_or_404(request.user.friendship_requests_received, id=friendship_request_id)
f_request.mark_viewed()
```
**Mark as viewed** a **list** of request / call `mark_viewed()` on each request in a list
```
Friend.objects.mark_as_viewed(friendship_requests_list)
```
## Getting data in a view

#### Required Imports
```
from friendship.models import Friend
```
####Friends

List of the current user's friends as User objects
```
all_friends = Friend.objects.friends(user)
```
Count of the current user's friends
```
friend_count = Friend.objects.friend_count(user)
```
Bool, True if two users are friends
```
is_friend = Friend.objects.are_friends(user1, user2):
```
#### Friendship Requests

List of all received friendship requests
```
requests_received = Friend.objects.received_requests(user)
```
List of all pending recieved friendship requests (all that have not been rejected)
```
requests_received = Friend.objects.pending_received_requests(user)
```
Count of all pending recieved friendship requests  (all that have not been rejected)
```
count = Friend.objects.pending_received_request_count(user)
```
List of all unread recieved friendship requests
```
requests_received = Friend.objects.unread_received_requests(user)
```
Count of all unread recieved friendship requests
```
requests_received = Friend.objects.unread_received_request_count(user)
```
List of all read recieved friendship requests
```
requests_received = Friend.objects.read_received_requests(user)
```
List of all rejected recieved friendship requests
```
requests_received = Friend.objects.rejected_received_requests(user)
```
List of all sent friendship requests
```
requests_sent = Friend.objects.sent_requests(user)
```
Bool, True if FriendshipRequest sent from user1 to user2
```
have_sent = Friend.objects.have_sent_request(user1, user2)
```
Bool, True if FriendshipRequest received by user1 from user2
```
have_received = Friend.objects.have_received_request(user1, user2)
```
Bool, True if FriendshipRequest exists between user1 and user2 (in either direction)
```
exists = Friend.objects.request_exists_between(user1, user2)
```
## Errors
Attempting to create an already existing friendship will raise
`friendship.exceptions.AlreadyExistsError`, a subclass of `django.db.IntegrityError`.

## Signals
```
friendship_request_created
friendship_request_rejected
friendship_request_canceled
friendship_request_accepted
friendship_removed
```
## Compatibility

I've been using Django 1.8 and Python 3.4. If your require backwards compatibility, please contribute!