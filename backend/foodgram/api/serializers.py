# import datetime
# from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from recipes.models import Favorite, Ingredient, Recipe, Tag
from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        max_length=254)
    username = serializers.CharField(
        required=True,
        max_length=150,
        min_length=3,
        allow_blank=False)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',)

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Такой пользователь уже существует')
        if username == 'me':
            raise ValidationError('Данный юзернейм недоступен')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return data

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(
            author_id=obj.id, user_id=user.id
        ).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

"""
class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        max_length=254)
    username = serializers.CharField(
        required=True,
        max_length=150,
        min_length=3,
        allow_blank=False)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',)

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Такой пользователь уже существует')
        if username == 'me':
            raise ValidationError('Данный юзернейм недоступен')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return data

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(
            author_id=obj.id, user_id=user.id
        ).exists()
"""

class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    author = UserSerializer(required=False)
    ingredients = RecipeIngredientSerializer(many=True, required=False)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(
            recipe_id=obj.id, user_id=user.id
        ).exists()


# неправильно работает
class SubscriptionSerializer(serializers.ModelSerializer):
    author = UserSerializer(required=False)
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('author', 'recipes')

    def get_recipes(self, obj):
        return Recipe.objects.filter(
            author_id=obj.id
        )
