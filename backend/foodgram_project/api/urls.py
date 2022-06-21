from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register(
    r'ingredients',
    views.IngredientViewSet,
    basename='ingredients'
)
router_v1.register(
    r'tags',
    views.TagViewSet,
    basename='tags'
)
router_v1.register(
    r'recipes',
    views.RecipeViewSet,
    basename='recipes'
)
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    views.FavoriteViewSet, basename='favorite'
)
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    views.ShoppingCartViewSet, basename='add_shopping_cart'
)


urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        views.DownloadShoppingCart.as_view(),
        name='download_shopping_cart'
    ),
    path('', include(router_v1.urls))
]
