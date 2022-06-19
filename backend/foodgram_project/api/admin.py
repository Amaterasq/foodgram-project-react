from api import models
from django.contrib import admin


class TagInline(admin.StackedInline):
    model = models.TagsRecipe
    extra = 1


class IngredientInline(admin.StackedInline):
    model = models.RecipeIngredient
    extra = 1


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name', 'color', 'slug')


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (TagInline, IngredientInline,)

    list_display = (
        'name',
        'author',
    )
    list_filter = ('tags',)
    search_fields = (
        'author__username',
        'author__email',
        'name',
    )


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    search_fields = (
        'user__username',
        'user__email',
        'recipe__name',
    )


@admin.register(models.ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    search_fields = (
        'user__username',
        'user__email',
        'recipe__name',
    )
