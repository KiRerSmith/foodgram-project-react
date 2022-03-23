# import datetime
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.db import IntegrityError, transaction
from importlib_metadata import requires
from djoser.conf import settings
from drf_extra_fields.fields import Base64ImageField
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


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    default_error_messages = {
        "cannot_create_user": settings.CONSTANTS.messages.CANNOT_CREATE_USER_ERROR
    }

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.LOGIN_FIELD,
            settings.USER_ID_FIELD,
            "password",
        )

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get("password")

        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error["non_field_errors"]}
            )

        return attrs

    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            self.fail("cannot_create_user")

        return user

    def perform_create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            if settings.SEND_ACTIVATION_EMAIL:
                user.is_active = False
                user.save(update_fields=["is_active"])
        return user


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class CustomImageField(serializers.Field):

    def to_internal_value(self, data):
        return data.decode('base64')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    author = UserSerializer(required=False)
    ingredients = RecipeIngredientSerializer(many=True, required=False)
    image = CustomImageField(required=False)
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


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = CreateRecipeIngredientSerializer(many=True, required=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 
                  'image', 'name', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        list = []
        for i in range(len(ingredients_data)):
            list.append(ingredients_data[i]['id'])
        ingredients = Ingredient.objects.filter(id__in=list)
        print(ingredients)
        recipe = Recipe.objects.create(**validated_data)
        recipe.ingredients.set()
        return recipe


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = ('id', 'recipe')

    def get_recipe(self, obj):
        return obj.id

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