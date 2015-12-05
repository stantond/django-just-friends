from django.conf.urls import url


urlpatterns = [
    url(r'^friendship/request/(?P<to_username>[\w.@+-]+)/$', 'friendship.views.request', name='request'),
    url(r'^friendship/cancel/(?P<friendship_request_id>\d+)/$', 'friendship.views.cancel', name='cancel'),
    url(r'^friendship/accept/(?P<friendship_request_id>\d+)/$', 'friendship.views.accept', name='accept'),
    url(r'^friendship/reject/(?P<friendship_request_id>\d+)/$', 'friendship.views.reject', name='reject'),
    url(r'^friendship/unfriend/(?P<to_username>[\w.@+-]+)/$', 'friendship.views.unfriend', name='unfriend'),
]
