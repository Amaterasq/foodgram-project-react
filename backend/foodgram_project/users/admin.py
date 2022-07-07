from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Follow, User

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = (
        'username',
        'email',
    )
    list_filter = (
        'username',
        'email',
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'following',
    )
    search_fields = (
        'user',
        'following',
    )
    list_filter = (
        'user',
        'following',
    )
