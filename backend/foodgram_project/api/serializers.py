from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import serializers

from api.models import (
    Favorite,
    Ingredient,
    Tag,
    Recipe,
    RecipeIngredient,
    ShoppingCart
)
from api.fields import Base64ImageField
from users.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.StringRelatedField(source='ingredient.id')
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='ingredient',
        many=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def get_is_favorited(self, obj):
        recipe = obj.id
        request = self.context.get('request')
        user = request.user.id
        return Favorite.objects.filter(
            user_id=user, recipe_id=recipe
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        recipe = obj.id
        request = self.context.get('request')
        user = request.user.id
        return ShoppingCart.objects.filter(
            user_id=user, recipe_id=recipe
        ).exists()


class RecipeIngredientCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)

    def validate_amount(self, value):
        if value < 0:
            raise serializers.ValidationError(
                'Количество ингредиента не может быть меньше 0!'
            )
        return value


class RecipeCreateSerializer(RecipeSerializer):
    ingredients = RecipeIngredientCreateSerializer(
        many=True,
        write_only=True
    )
    tags = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=Tag.objects.all()
        ),
        write_only=True
    )

    def _is_amount_valid(self, ingredient):
        amount = ingredient.get('amount')
        if ingredient.get('amount') <= 0:
            raise serializers.ValidationError(
                'Количество ингредиента не может быть меньше/равно 0'
            )
        return amount

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            recipe.tags.add(tag)

        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredient,
                id=ingredient.get('id')
            )
            amount = self._is_amount_valid(ingredient)
            RecipeIngredient.objects.create(
                ingredient=current_ingredient,
                amount=amount,
                recipe=recipe
            )

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        for tag in tags:
            instance.tags.add(tag)

        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredient,
                id=ingredient.get('id')
            )
            amount = self._is_amount_valid(ingredient)
            RecipeIngredient.objects.create(
                ingredient=current_ingredient,
                amount=amount,
                recipe=instance
            )
        return super().update(instance, validated_data)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )


class FavoriteCreateSerializer(serializers.ModelSerializer):
    id = serializers.StringRelatedField(
        source='recipe.id',
        read_only=True
    )
    name = serializers.StringRelatedField(
        source='recipe.name',
        read_only=True
    )
    image = serializers.StringRelatedField(
        source='recipe.image',
        read_only=True
    )
    cooking_time = serializers.StringRelatedField(
        source='recipe.cooking_time',
        read_only=True
    )

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = ('user', 'recipe',)


class ShoppingCartCreateSerializer(FavoriteCreateSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time',)
