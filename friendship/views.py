from django.contrib.auth.decorators import login_required
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect

from .exceptions import AlreadyExistsError
from .models import Friend


@login_required
def request(request, to_username):
    if request.GET.get('from'):
        context = {}
        try:
            to_user = get_object_or_404(User, username=to_username)
            Friend.objects.add_friendship_request(request.user, to_user)
        except AlreadyExistsError as e:
            context = {'errors': ["%s" % e]}
        return redirect(request.GET.get('from'), context)
    else:
        return redirect('/')


@login_required
def cancel(request, friendship_request_id):
    if request.GET.get('from'):
        f_request = get_object_or_404(
            request.user.friendship_requests_sent,
            id=friendship_request_id)
        f_request.cancel()
        return redirect(request.GET.get('from'))
    else:
        return redirect('/')


@login_required
def accept(request, friendship_request_id):
    if request.GET.get('from'):
        f_request = get_object_or_404(
            request.user.friendship_requests_received,
            id=friendship_request_id)
        f_request.accept()
        return redirect(request.GET.get('from'))
    else:
        return redirect('/')


@login_required
def reject(request, friendship_request_id):
    if request.GET.get('from'):
        f_request = get_object_or_404(
            request.user.friendship_requests_received,
            id=friendship_request_id)
        f_request.reject()
        return redirect(request.GET.get('from'))
    else:
        return redirect('/')


@login_required
def unfriend(request, to_username):
    if request.GET.get('from'):
        to_user = get_object_or_404(User, username=to_username)
        Friend.objects.unfriend(request.user, to_user)
        return redirect(request.GET.get('from'))
    else:
        return redirect('/')
