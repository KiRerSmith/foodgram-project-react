from django.http import HttpResponse
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404
from django_filters.filters import CharFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import filters, mixins, serializers, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Follow, User

from .pagination import UserPagination
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsOwnerAdminModeratorOrReadOnly)
from .serializers import (CreateRecipeSerializer, FavoriteRecipeSerializer,
                          FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserSerializer)

from djoser import utils
from djoser.conf import settings
from djoser.compat import get_user_email


@api_view(['POST', 'DELETE'])
def favorite(request, recipe_id):
    if request.method == 'DELETE':
        favorite = get_object_or_404(
            Favorite,
            user=request.user,
            recipe__id=recipe_id
        )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    elif request.method == 'POST':
        serializer = FavoriteSerializer(data=request.data)
        if serializer.is_valid():
            recipe = get_object_or_404(Recipe, pk=recipe_id)
            if Favorite.objects.filter(user=request.user, recipe=recipe):
                raise serializers.ValidationError(
                    'Нельзя добавить больше одного избранного!')
            serializer.save(user=request.user,
                            recipe_id=recipe_id)
            print_serializer = FavoriteRecipeSerializer(recipe)
            return Response(
                print_serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'DELETE'])
def shopping_cart(request, recipe_id):
    if request.method == 'DELETE':
        shopping_cart = get_object_or_404(
            ShoppingCart,
            user=request.user,
            recipe__id=recipe_id
        )
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    elif request.method == 'POST':
        serializer = ShoppingCartSerializer(data=request.data)
        if serializer.is_valid():
            recipe = get_object_or_404(Recipe, pk=recipe_id)
            if ShoppingCart.objects.filter(user=request.user, recipe=recipe):
                raise serializers.ValidationError(
                    'Нельзя добавить больше одного рецепта в список!')
            serializer.save(user=request.user,
                            recipe_id=recipe_id)
            print_serializer = FavoriteRecipeSerializer(recipe)
            return Response(
                print_serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'DELETE'])
def subscribe(request, author_id):
    if request.method == 'DELETE':
        subscription = get_object_or_404(
            Follow,
            user=request.user,
            author__id=author_id
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    elif request.method == 'POST':
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            author = get_object_or_404(User, id=author_id)
            if Follow.objects.filter(user=request.user, author_id=author_id):
                raise serializers.ValidationError(
                    'Нельзя добавить больше одной подписки!')
            serializer.save(user=request.user,
                            author_id=author_id)
            # serializer = SubscriptionSerializer(author)
            # не работает сериализатор в ответ - не находит юзера запроса
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def download_shopping_cart(request):
    user = request.user
    shopping_cart_list = list(user.buyer.all().values())
    recipe_id_list = []
    for element in shopping_cart_list:
        recipe_id_list.append(element['recipe_id'])
    ingredients_queryset = Recipe.ingredients.through.objects.filter(
        recipe_id__in=recipe_id_list
    ).values()
    shop_list = []
    for i in range(ingredients_queryset.count()):
        ingr_list = []
        ingr = ingredients_queryset[i]
        if ingr['ingredient_id'] in shop_list:
            ix = shop_list.index(ingr['ingredient_id'])
            shop_list[ix+1][2] = str(int(shop_list[ix+1][2]) + ingr['amount'])
        else:
            ingredient = Ingredient.objects.get(
                id=ingr['ingredient_id']
            )
            ingr_list.append(ingredient.name.capitalize())
            ingr_list.append(f'({ingredient.measurement_unit}) -')
            ingr_list.append(str(ingr['amount']))
            shop_list.append(ingr['ingredient_id'])
            shop_list.append(ingr_list)
    file = open('shop_list.txt', 'w')
    for j in range(len(shop_list) // 2):
        file.write(' '.join(shop_list[j * 2 + 1]))
        file.write("\n")
    file.close()
    file = open('shop_list.txt', 'r')
    response = HttpResponse(
        file.read(),
        content_type='text/plain; charset=UTF-8'
    )
    response['Content-Disposition'] = ('attachment; filename="shop_list.txt"')

    return response


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination
    # (IsAdmin,)
    # permission_classes = [IsOwnerAdminModeratorOrReadOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    # lookup_field = 'username'

    def retrieve(self, request, pk=None):
        queryset = User.objects.filter(pk=pk)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def get_serializer_class(self):
        if self.action == "create":
            return settings.SERIALIZERS.user_create
        elif self.action == "set_password":
            if settings.SET_PASSWORD_RETYPE:
                return settings.SERIALIZERS.set_password_retype
            return settings.SERIALIZERS.set_password
        return UserSerializer

    @action(detail=False)
    def me(self, request):
        request_user = request.user
        queryset = User.objects.filter(id=request_user.id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": self.request.user}
            to = [get_user_email(self.request.user)]
            settings.EMAIL.password_changed_confirmation(
                self.request,
                context
            ).send(to)

        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            utils.logout_user(self.request)
        elif settings.CREATE_SESSION_ON_LOGIN:
            update_session_auth_hash(self.request, self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeFilter(FilterSet):
    tags = CharFilter(field_name='tags__slug')
    author = CharFilter(field_name='author__slug')

    class Meta:
        model = Recipe
        fields = ['author', 'tags']


class RecipeViewSet(viewsets.ModelViewSet):
    # queryset = Recipe.objects.all()
    # serializer_class = RecipeSerializer
    pagination_class = UserPagination
    permission_classes = [IsOwnerAdminModeratorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_queryset(self):
        # queryset = Recipe.objects.all()
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        if is_favorited is not None and is_favorited == '1':
            favorited = Favorite.objects.filter(user=self.request.user)
            recipes_id = []
            for i in range(favorited.count()):
                recipes_id.append(favorited.values()[i]['recipe_id'])
            return Recipe.objects.filter(id__in=recipes_id)
        if is_in_shopping_cart is not None and is_in_shopping_cart == '1':
            shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
            recipes_id = []
            for i in range(shopping_cart.count()):
                recipes_id.append(shopping_cart.values()[i]['recipe_id'])
            return Recipe.objects.filter(id__in=recipes_id)
        return Recipe.objects.all()

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        instance_serializer = RecipeSerializer(
            instance, context={'request': request}
        )
        return Response(instance_serializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.queryset.get(pk=kwargs.get('pk'))
        serializer = CreateRecipeSerializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        instance_serializer = RecipeSerializer(
            instance, context={'request': request}
        )
        return Response(instance_serializer.data)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CreateRecipeSerializer
        return RecipeSerializer


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # pagination_class = UserPagination
    permission_classes = [IsOwnerAdminModeratorOrReadOnly]


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # pagination_class = UserPagination
    permission_classes = [IsOwnerAdminModeratorOrReadOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class SubscriptionViewSet(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = SubscriptionSerializer
    pagination_class = UserPagination
    permission_classes = [IsOwnerAdminModeratorOrReadOnly]
    http_method_names = ['get']

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)
