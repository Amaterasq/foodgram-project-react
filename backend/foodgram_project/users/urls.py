from django.conf.urls import url
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users import views

app_name = 'users'

users_router = DefaultRouter()

users_router.register(
    r'subscriptions',
    views.SubscriptionViewset,
    basename='subscriptions'
)
users_router.register(
    r'(?P<author_id>\d+)/subscribe',
    views.SubscriptionCreateDestroy,
    basename='subscribe'
)


urlpatterns = [
    path('users/', include(users_router.urls)),
    path(
        'users/',
        views.UserViewSet.as_view(
            {'get': 'list', 'post': 'create'}
        ),
        name='get_create_user'
    ),
    path('', include('djoser.urls')),
    url(r'^auth/', include('djoser.urls.authtoken')),
]
