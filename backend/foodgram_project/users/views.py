from django.shortcuts import get_object_or_404

from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from djoser.views import UserViewSet as DjoserUserViewset

from users.models import User, Follow
from users.paginations import LimitResultsSetPagination
from users.serializers import SubscriptionSerializer, UserSerializer


class UserViewSet(DjoserUserViewset):
    pagination_class = LimitResultsSetPagination

    def list(self, request):
        queryset = User.objects.all()
        page = self.paginate_queryset(queryset)
        serializer = UserSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class SubscriptionViewset(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Возвращает подписки текущего пользователя"""
    serializer_class = SubscriptionSerializer
    pagination_class = LimitResultsSetPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Follow.objects.filter(user=user)


class SubscriptionCreateDestroy(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Создание и удаление подписок."""
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['author'] = int(self.kwargs.get('author_id'))
        return context

    def perform_create(self, serializer):
        author = get_object_or_404(
            User,
            id=self.kwargs.get('author_id')
        )
        serializer.save(user=self.request.user, author=author)

    @action(methods=['delete'], detail=False)
    def delete(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Follow,
            author=self.kwargs.get('author_id'),
            user=request.user.id
        )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
