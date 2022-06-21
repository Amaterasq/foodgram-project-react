from django.shortcuts import get_object_or_404
from djoser.serializers import TokenCreateSerializer, UserCreateSerializer
from rest_framework import serializers

from api.models import Recipe
from users.exceptions import FollowValidationError
from users.models import Follow, User


class UserRegistrationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class TokenRegistrationSerializer(TokenCreateSerializer):
    class Meta:
        fields = ('password', 'email',)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        user = request.user
        author = obj
        return Follow.objects.filter(user=user, author=author).exists()


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    """Сокращенный вариант сериализатора рецепта."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.StringRelatedField(
        source='author.email',
        read_only=True
    )
    id = serializers.PrimaryKeyRelatedField(
        source='author.id',
        read_only=True
    )
    username = serializers.StringRelatedField(
        source='author.username',
        read_only=True
    )
    first_name = serializers.StringRelatedField(
        source='author.first_name',
        read_only=True
    )
    last_name = serializers.StringRelatedField(
        source='author.last_name',
        read_only=True
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipe.count')

    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request:
            user = request.user
            author = obj.author
            return Follow.objects.filter(user=user, author=author).exists()
        return False

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.author)
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        if limit is not None:
            try:
                limit = int(limit)
                queryset = queryset[:limit]
            except ValueError:
                raise ValueError(
                    detail='Ошибка в получении queryset-limit'
                )
        serializer = SubscriptionRecipeSerializer(queryset, many=True)
        return serializer.data

    def validate(self, data):
        """Валидация некорректных вариантов подписки."""
        author = get_object_or_404(User, id=self.context['author'])
        if self.context['request'].user == author:
            raise FollowValidationError(
                detail='Нельзя подписываться на самого себя'
            )
        if Follow.objects.filter(
            user=self.context['request'].user,
            author=author
        ).exists():
            raise FollowValidationError(
                f'Вы уже подписаны на {author.username}'
            )
        return data
