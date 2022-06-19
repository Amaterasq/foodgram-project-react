from django.contrib import admin
from django.contrib.auth.models import Group
from users.models import Follow, User

admin.site.unregister(Group)


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'is_superuser',
    )
    search_fields = ('email', 'username',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    search_fields = (
        'user__username',
        'author__username',
        'user__email',
        'author__email',
    )
