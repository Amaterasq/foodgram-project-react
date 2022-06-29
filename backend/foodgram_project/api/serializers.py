from collections import OrderedDict

#  from django.core.exceptions import ValidationError
#  from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api.fields import Base64ImageField
from api.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                        ShoppingCart, Tag)
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
    '''Сериализатор отображения рецепта'''
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='ingredient',
        many=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=True)

    def get_is_favorited(self, obj):
        recipe_id = obj.id
        request = self.context.get('request')
        user_id = request.user.id
        return Favorite.objects.filter(
            user_id=user_id,
            recipe_id=recipe_id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        recipe_id = obj.id
        request = self.context.get('request')
        user_id = request.user.id
        return ShoppingCart.objects.filter(
            user_id=user_id,
            recipe_id=recipe_id
        ).exists()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )


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

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    '''
    def validate_ingredients(self, attrs):
        id_list = []
        for attr in attrs:
            attr_amount = dict(attr)['amount']
            if attr_amount < 1:
                raise ValidationError('Количество должно быть больше 0')
            id_list.append(dict(attr)['ingredient']['id'])
        id_list_set = set(id_list)
        if len(attrs) == len(id_list_set):
            return attrs
        raise ValidationError('Ингредиенты не уникальны')
    '''

    def to_representation(self, instance):
        '''Изменение сериализатора отображения'''
        ret = OrderedDict()
        fields = RecipeSerializer(instance, context=self.context)

        for field in fields:
            attribute = field.get_attribute(instance)
            if attribute is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)
        return ret

    def add_ingredients(self, ingredients, recipes):
        RecipeIngredient.objects.bulk_create([RecipeIngredient(
            ingredient=dict(ingredient)['ingredient'],
            recipe=recipes,
            amount=dict(ingredient)['amount'],
        ) for ingredient in ingredients])
        return recipes

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipes = Recipe.objects.create(**validated_data)
        recipes.tags.set(tags)
        return self.add_ingredients(ingredients, recipes)

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipe')
        tags = validated_data.pop('tags')
        super().update(instance, validated_data)
        instance.tags.set(tags)
        instance.ingredients.clear()
        return self.add_ingredients(ingredients, instance)


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
