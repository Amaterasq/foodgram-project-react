from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from api.models import Recipe, Favorite, ShoppingCart


class CreateDestroyMixin(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    '''Миксин для наследования FavoriteViewSet, ShoppingCartViewSet'''

    def add_obj(self, request, model, *args, **kwargs):
        recipe = get_object_or_404(
            Recipe, id=self.kwargs.get('recipe_id')
        )
        user = self.request.user
        if model == ShoppingCart:
            in_shopping_cart = ShoppingCart.objects.filter(
                user=user, recipe=recipe).exists()
            if in_shopping_cart:
                content = {
                    'error': f'{recipe.name} уже добавлен в корзину покупок!'
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        elif model == Favorite:
            in_favorite = Favorite.objects.filter(
                user=user, recipe=recipe).exists()
            if in_favorite:
                content = {
                    'error': f'{recipe.name} уже был добавлен в избранное'
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        recipe = get_object_or_404(
            Recipe, id=self.kwargs.get('recipe_id')
        )
        serializer.save(user=self.request.user, recipe=recipe)

    def del_obj(self, request, model, *args, **kwargs):
        instance = get_object_or_404(
            model,
            recipe=self.kwargs.get('recipe_id'),
            user=request.user.id
        )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
