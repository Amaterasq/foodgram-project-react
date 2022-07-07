from django.urls import include, path

from users.views import FollowApiView, FollowListAPIView

urlpatterns = [
    path(
        'users/<int:id>/subscribe/',
        FollowApiView.as_view(),
        name='subscribe'
    ),
    path(
        'users/subscriptions/',
        FollowListAPIView.as_view(),
        name='subscription'
    ),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]
