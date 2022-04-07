from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from djoser.conf import settings
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.serializers import ValidationError
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
            raise ValidationError(
                {'errors': 'Такой пользователь уже существует'}
            )
        if username == 'me':
            raise ValidationError(
                {'errors': 'Данный юзернейм недоступен'}
            )
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                {'errors': 'Пользователь с таким email уже существует'}
            )
        return data

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(
            author_id=obj.id, user_id=user.id
        ).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    msg = settings.CONSTANTS.messages.CANNOT_CREATE_USER_ERROR
    default_error_messages = {
        'cannot_create_user': msg
    }

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.LOGIN_FIELD,
            settings.USER_ID_FIELD,
            'password',
        )

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get('password')

        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {'password': serializer_error['non_field_errors']}
            )

        return attrs

    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            self.fail('cannot_create_user')

        return user

    def perform_create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            if settings.SEND_ACTIVATION_EMAIL:
                user.is_active = False
                user.save(update_fields=['is_active'])
        return user


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_amount(self, obj):
        recipe_id = self.context.get('recipe_id')
        ingredient_id = obj.id
        ingredient_amount = get_object_or_404(
            IngredientAmount,
            ingredient_id=ingredient_id,
            recipe_id=recipe_id
        )
        return ingredient_amount.amount


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=True)
    author = UserSerializer(required=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(
            recipe_id=obj.id, user_id=user.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            recipe_id=obj.id, user_id=user.id
        ).exists()

    def get_ingredients(self, obj):
        return RecipeIngredientSerializer(obj.ingredients.all(), many=True,
                                          context={'recipe_id': obj.id}).data


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = CreateRecipeIngredientSerializer(many=True, required=True)
    image = Base64ImageField(max_length=None, use_url=False)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags',
                  'image', 'name', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        ingredients_list = []
        amount_list = []
        for i in range(len(ingredients_data)):
            ingredients_list.append(ingredients_data[i]['id'])
            amount_list.append(ingredients_data[i]['amount'])
        ingredients = Ingredient.objects.filter(id__in=ingredients_list)
        tags = Tag.objects.filter(name__in=tags_data)
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for j in range(len(ingredients_data)):
            recipe.ingredients.add(
                ingredients[j], through_defaults={
                    'amount': amount_list[j]
                    }
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        ingredients_list = []
        amount_list = []
        for i in range(len(ingredients_data)):
            ingredients_list.append(ingredients_data[i]['id'])
            amount_list.append(ingredients_data[i]['amount'])
        instance.ingredients.clear()
        ingredients = Ingredient.objects.filter(id__in=ingredients_list)
        tags = Tag.objects.filter(name__in=tags_data)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.tags.set(tags)
        instance.save()
        for j in range(len(ingredients_data)):
            instance.ingredients.add(
                ingredients[j], through_defaults={
                    'amount': amount_list[j]
                    }
            )
        return instance

    def get_ingredients(self, obj):
        return CreateRecipeIngredientSerializer(
            self.data.get('ingredients'),
            many=True,
            context={'recipe_id': obj.id}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = ('id', 'recipe')

    def get_recipe(self, obj):
        return obj.id


class ShoppingCartSerializer(serializers.ModelSerializer):
    recipe = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = ('id', 'recipe')

    def get_recipe(self, obj):
        return obj.id


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='author.email', required=False)
    id = serializers.IntegerField(source='author.id', required=False)
    username = serializers.CharField(
        source='author.username',
        required=False
    )
    first_name = serializers.CharField(
        source='author.first_name',
        required=False
    )
    last_name = serializers.CharField(
        source='author.last_name',
        required=False
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',)

    def validate(self, data):
        request_user = self.context.get('request').user
        author_id = data.get('id')
        if request_user.id == author_id:
            raise ValidationError({'errors': 'Нельзя подписываться на себя!'})
        return data

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(
            author_id=obj.id, user_id=user.id
        ).exists()

    def get_recipes(self, obj):
        limit = self.context.get('request').query_params.get('recipes_limit')
        if limit is not None:
            limit = int(limit)
        else:
            limit = 2
        queryset = obj.author.recipes.all()[:limit]
        return FavoriteRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.all().count()
