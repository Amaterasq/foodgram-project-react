from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.views import APIView

from api.filters import IngredientFilter, RecipeFilter
from api.mixins import CreateDestroyMixin
from api.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                        ShoppingCart, Tag)
from api.paginations import LimitResultsSetPagination
from api.permissions import OwnerAdminReadOnly
from api.serializers import (FavoriteCreateSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeSerializer,
                             ShoppingCartCreateSerializer, TagSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    #  permission_classes = (IsAdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    #  permission_classes = (IsAdminOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    permission_classes = (OwnerAdminReadOnly,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FavoriteViewSet(CreateDestroyMixin):
    serializer_class = FavoriteCreateSerializer
    model = Favorite

    def create(self, request, *args, **kwargs):
        return self.add_obj(request, self.model, *args, **kwargs)

    @action(methods=['delete'], detail=False)
    def delete(self, request, *args, **kwargs):
        return self.del_obj(request, self.model, *args, **kwargs)


class ShoppingCartViewSet(CreateDestroyMixin):
    serializer_class = ShoppingCartCreateSerializer
    model = ShoppingCart

    def create(self, request, *args, **kwargs):
        return self.add_obj(request, self.model, *args, **kwargs)

    @action(methods=['delete'], detail=False)
    def delete(self, request, *args, **kwargs):
        return self.del_obj(request, self.model, *args, **kwargs)


class DownloadShoppingCart(APIView):
    permission_classes = (IsAuthenticated,)

    def _create_shopping_list(self, request, response):
        unique_ingredient = []
        response.write('Список продуктов:\n')
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values_list(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(total_amount=Sum('amount'))
        for item in ingredients:
            if item.ingredient.id not in unique_ingredient:
                response.write(f'\n{item.ingredient._get_name()}')
                response.write(f' - {item.ingredient["total_amount"]}')
                unique_ingredient.append(item.ingredient.id)
        return response

    def get(self, request):
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; filename="{settings.SHOPPING_LIST_NAME}"'
        )
        return self._create_shopping_list(self.get_queryset(), response)

    def get_queryset(self):
        user = self.request.user
        return user.shopping_cart.all()
