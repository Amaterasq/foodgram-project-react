from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.views import APIView

from api.serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    FavoriteCreateSerializer,
    ShoppingCartCreateSerializer,
)
from api.models import (
    Ingredient,
    Tag,
    Recipe,
    Favorite,
    ShoppingCart,
    RecipeIngredient
)
from api.filters import IngredientFilter, RecipeFilter
from api.paginations import LimitResultsSetPagination
from api.permissions import OwnerAdminReadOnly, IsAdminOrReadOnly


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    pagination_class = LimitResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (OwnerAdminReadOnly,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = RecipeSerializer(
            instance=serializer.instance,
            context={'request': self.request}
        )
        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        serializer = RecipeSerializer(
            instance=serializer.instance,
            context={'request': self.request},
        )
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )

    def get_queryset(self):
        queryset = Recipe.objects.all()
        user = self.request.user
        is_favorited = self.request.query_params.get(
            'is_favorited'
        )
        is_in_shopping_cart = (
            self.request.query_params.get('is_in_shopping_cart')
        )

        if is_favorited == '1':
            queryset = queryset.filter(favorite__user=user)
        if is_in_shopping_cart == '1':
            queryset = queryset.filter(shopping_cart__user=user)

        return queryset


class FavoriteViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = FavoriteCreateSerializer

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(
            Recipe, id=self.kwargs.get('recipe_id')
        )
        user = self.request.user
        in_favorite = Favorite.objects.filter(
            user=user, recipe=recipe).exists()
        if in_favorite:
            content = {'error': f'{recipe.name} уже был добавлен в избранное'}
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

    @action(methods=['delete'], detail=False)
    def delete(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Favorite,
            recipe=self.kwargs.get('recipe_id'),
            user=request.user.id
        )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ShoppingCartCreateSerializer

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(
            Recipe, id=self.kwargs.get('recipe_id')
        )
        user = self.request.user
        in_shopping_cart = ShoppingCart.objects.filter(
            user=user, recipe=recipe).exists()
        if in_shopping_cart:
            content = {
                'error': f'{recipe.name} уже добавлен в корзину покупок!'
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

    @action(methods=['delete'], detail=False)
    def delete(self, request, *args, **kwargs):
        instance = get_object_or_404(
            ShoppingCart,
            recipe=self.kwargs.get('recipe_id'),
            user=request.user.id
        )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCart(APIView):
    permission_classes = (IsAuthenticated,)

    def _create_shopping_list(self, queryset, response):
        unique_ingredient = []
        response.write('Список продуктов:\n')
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=queryset.values("recipe")
        )
        for item in ingredients:
            if item.ingredient.id not in unique_ingredient:
                total_amount = RecipeIngredient.objects.filter(
                    ingredient__id=item.ingredient.id
                ).aggregate(Sum('amount'))
                response.write(f'\n{item.ingredient._get_name()}')
                response.write(f' - {total_amount.get("amount__sum")}')
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
