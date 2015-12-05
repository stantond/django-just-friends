from __future__ import unicode_literals
from django.db import models
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ValidationError

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from friendship.exceptions import AlreadyExistsError
from friendship.signals import friendship_request_created, \
    friendship_request_rejected, friendship_request_canceled, \
    friendship_request_viewed, friendship_request_accepted, friendship_removed

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
REJECTED_FRIENDSHIP_REQUEST_EXPIRY = 1


@python_2_unicode_compatible
class FriendshipRequest(models.Model):
    """ Model to represent friendship requests
    Many-to-Many
    User-to-User
    """
    from_user = models.ForeignKey(AUTH_USER_MODEL, related_name='friendship_requests_sent')
    to_user = models.ForeignKey(AUTH_USER_MODEL, related_name='friendship_requests_received')
    message = models.TextField(_('Message'), blank=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    viewed = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _('Friendship Request')
        verbose_name_plural = _('Friendship Requests')
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return "Request from #%d to #%d" % (self.from_user_id, self.to_user_id)

    def accept(self):
        """ `to_user` accepts this friendship request
        Creates a Friendship relation in each direction, then deletes self
        """
        relation1 = Friend.objects.create(
            from_user=self.from_user,
            to_user=self.to_user
        )

        relation2 = Friend.objects.create(
            from_user=self.to_user,
            to_user=self.from_user
        )

        friendship_request_accepted.send(
            sender=self,
            from_user=self.from_user,
            to_user=self.to_user
        )

        self.delete()

        # Delete any reverse requests WHY IS THIS REQUIRED?
        FriendshipRequest.objects.filter(
            from_user=self.to_user,
            to_user=self.from_user
        ).delete()

        return True

    def reject(self):
        """ `to_user` rejects this friendship request """
        self.delete()
        friendship_request_rejected.send(sender=self)

    def cancel(self):
        """ `from_user` cancels this friendship request """
        self.delete()
        friendship_request_canceled.send(sender=self)
        return True

    def mark_viewed(self):
        self.viewed = timezone.now()
        friendship_request_viewed.send(sender=self)
        self.save()
        return True


class FriendshipManager(models.Manager):
    """ Friendship manager """

    def friends(self, user):
        """ Return a list of all friends """
        qs = Friend.objects.select_related('from_user', 'to_user').filter(
            to_user=user).all()
        return [u.from_user for u in qs]

    def friend_count(self, user):
        """ Return a count of all friends """
        return Friend.objects.select_related('from_user', 'to_user').filter(
            to_user=user).count()

    def mark_as_viewed(self, friendship_requests):
        """ Calls mark_viewed on each FriendshipRequest a given list """
        for request in friendship_requests:
            request.mark_viewed()

    def received_requests(self, user):
        """ Return a list of friendship requests """
        qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
            to_user=user).all()
        return list(qs)

    def sent_requests(self, user):
        """ Return a list of friendship requests from user """
        qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
            from_user=user).all()
        return list(qs)

    def unread_received_requests(self, user):
        """ Return a list of unread friendship requests """
        qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
            to_user=user,
            viewed__isnull=True).all()
        return list(qs)

    def unread_received_request_count(self, user):
        """ Return a count of unread friendship requests """
        return FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
            to_user=user,
            viewed__isnull=True
            ).count()

    def read_received_requests(self, user):
        """ Return a list of read friendship requests """
        qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
            to_user=user,
            viewed__isnull=False).all()
        return list(qs)

    def pending_received_requests(self, user):
        """ All received friendship requests """
        qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
            to_user=user).all()
        return list(qs)

    def pending_received_request_count(self, user):
        """ Return a count of friendship requests """
        return FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
            to_user=user).count()

    def request_exists_directional(self, user1, user2):
        """ Does a FriendshipRequest from user1 to user2 exist? """
        try:
            FriendshipRequest.objects.get(from_user=user1, to_user=user2)
            return True
        except FriendshipRequest.DoesNotExist:
            return False

    def have_sent_request(self, user1, user2):
        """ Has user1 sent a request to user2? """
        return self.request_exists_directional(user1, user2)

    def have_received_request(self, user1, user2):
        """ Has user1 received a request from user 2? """
        return self.request_exists_directional(user2, user1)

    def request_exists_between(self, user1, user2):
        """ Does a FriendshipRequest between user1 and user2 exist? """
        if self.have_sent_request(user1, user2):
            return True
        if self.have_received_request(user1, user2):
            return True
        return False

    def add_friendship_request(self, from_user, to_user, message=None):
        """ Create a friendship request """
        if from_user == to_user:
            raise ValidationError("Users cannot be friends with themselves")
        if message is None:
            message = ''
        # TODO Check if reverse request exists first
        request, created = FriendshipRequest.objects.get_or_create(
            from_user=from_user,
            to_user=to_user,
            message=message,
        )
        if created is False:
            raise AlreadyExistsError("Friendship already requested")
        friendship_request_created.send(sender=request)
        return request

    def unfriend(self, to_user, from_user):
        """ Destroy a friendship relationship """
        try:
            qs = Friend.objects.filter(
                Q(to_user=to_user, from_user=from_user) |
                Q(to_user=from_user, from_user=to_user)
            ).distinct().all()

            if qs:
                friendship_removed.send(
                    sender=qs[0],
                    from_user=from_user,
                    to_user=to_user
                )
                qs.delete()
                return True
            else:
                return False
        except Friend.DoesNotExist:
            return False

    def are_friends(self, user1, user2):
        """ Are these two users friends? """
        try:
            Friend.objects.get(to_user=user1, from_user=user2)
            return True
        except Friend.DoesNotExist:
            return False


@python_2_unicode_compatible
class Friend(models.Model):
    """ Model to represent Friendships """
    from_user = models.ForeignKey(AUTH_USER_MODEL, related_name='_unused_')
    to_user = models.ForeignKey(AUTH_USER_MODEL, related_name='friends')
    created = models.DateTimeField(default=timezone.now)

    objects = FriendshipManager()

    class Meta:
        verbose_name = _('Friend')
        verbose_name_plural = _('Friends')
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return "Friendship from #%d to #%d" % (self.from_user_id, self.to_user_id)

    def save(self, *args, **kwargs):
        # Ensure users can't be friends with themselves
        if self.to_user == self.from_user:
            raise ValidationError("Users cannot be friends with themselves.")
        super(Friend, self).save(*args, **kwargs)
