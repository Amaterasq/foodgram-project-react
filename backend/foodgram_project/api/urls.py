from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientViewSet,
    TagViewSet,
    RecipeViewSet,
    FavoriteViewSet,
    ShoppingCartViewSet,
    DownloadShoppingCart,
)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
router_v1.register(
    r'tags',
    TagViewSet,
    basename='tags'
)
router_v1.register(
    r'recipes',
    RecipeViewSet,
    basename='recipes'
)
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteViewSet, basename='favorite'
)
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartViewSet, basename='add_shopping_cart'
)


urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        DownloadShoppingCart.as_view()
    ),
    path('', include(router_v1.urls))
]
