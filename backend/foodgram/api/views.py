# from urllib import request
from functools import partial
from msilib.schema import CreateFolder
from turtle import update
from venv import create
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.filters import CharFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
# from djoser.views import UserViewSet
from rest_framework import filters, mixins, serializers, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from recipes.models import Favorite, Ingredient, Recipe, Tag
from users.models import Follow, User
from foodgram.settings import ADMIN_EMAIL

from .pagination import UserPagination
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsOwnerAdminModeratorOrReadOnly)
from .serializers import (CreateRecipeSerializer, FavoriteRecipeSerializer, FavoriteSerializer, IngredientSerializer, RecipeSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserSerializer)

from djoser import signals, utils
from djoser.conf import settings
from djoser.compat import get_user_email
"""
confirmation_token = PasswordResetTokenGenerator()


@api_view(['POST'])
def create_and_get_code(request):
    serializer = CreateAndGetCode(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get('email')
    username = serializer.validated_data.get('username')
    obj, created = User.objects.get_or_create(username=username, email=email)
    if created is False:
        return Response(
            'Такой пользователь уже существует',
            status=status.HTTP_400_BAD_REQUEST)
    confirmation_code = confirmation_token.make_token(user=obj)
    message = f'Ваш код {confirmation_code}'
    send_mail(
        subject='Код подтверждения',
        message=message,
        from_email=ADMIN_EMAIL,
        recipient_list=[email]
    )
    return Response(
        {'email': f'{email}', 'username': f'{username}'},
        status=status.HTTP_200_OK)


@api_view(['POST'])
def get_token(request):
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    code = serializer.validated_data.get('confirmation_code')
    if not User.objects.filter(username=username).exists():
        return Response(
            'Пользователь не найден',
            status=status.HTTP_404_NOT_FOUND)
    user = get_object_or_404(User, username=username)
    if confirmation_token.check_token(user, code):
        token = AccessToken.for_user(user)
        return Response({'token': f'{token}'}, status=status.HTTP_200_OK)
    return Response(
        'Отсутствует обязательное поле или оно некорректно',
        status=status.HTTP_400_BAD_REQUEST)
"""

"""@api_view(['GET', 'POST'])
def get_subscriptions(request):
    if request.method == 'POST':
        serializer = SubscriptionSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    subscriptions = Follow.objects.filter(user_id=1)
    serializer = SubscriptionSerializer(subscriptions, many=True)
    return Response(serializer.data)"""
@api_view(['POST', 'DELETE'])
def favorite(request, recipe_id):
    if request.method == 'DELETE':
        favorite = get_object_or_404(Favorite, user=request.user, recipe__id=recipe_id)
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
            return Response(print_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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
            settings.EMAIL.password_changed_confirmation(self.request, context).send(to)

        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            utils.logout_user(self.request)
        elif settings.CREATE_SESSION_ON_LOGIN:
            update_session_auth_hash(self.request, self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

"""
class APIMe(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            user = get_object_or_404(User, id=request.user.id)
            serializer = MeSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            'Необходима авторизация',
            status=status.HTTP_401_UNAUTHORIZED)

    def patch(self, request):
        if request.user.is_authenticated:
            user = get_object_or_404(User, id=request.user.id)
            serializer = MeSerializer(user, request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        return Response(
            'Необходима авторизация',
            status=status.HTTP_401_UNAUTHORIZED)
"""

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    # serializer_class = RecipeSerializer
    pagination_class = UserPagination
    permission_classes = [IsOwnerAdminModeratorOrReadOnly]
    filter_backends = (DjangoFilterBackend, )

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CreateRecipeSerializer
        return RecipeSerializer


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = UserPagination
    permission_classes = [IsOwnerAdminModeratorOrReadOnly]


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = UserPagination
    permission_classes = [IsOwnerAdminModeratorOrReadOnly]

# не используется
class FavoriteViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):

    serializer_class = FavoriteSerializer
    permission_classes = [IsAdmin]
    # http_method_names = ['post', 'delete']

    # @action(detail=True, methods=['post'], url_path='favorite')
    def perform_create(self, serializer):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        user = self.request.user
        if Favorite.objects.filter(user=user, recipe=recipe):
            raise serializers.ValidationError(
                'Нельзя добавить больше одного избранного!')
        serializer.save(user=user,
                        recipe=recipe)
    
    def get_object(self):
        favorites = get_object_or_404(
            Favorite,
            recipe__id=self.kwargs['recipe_id'],
        )
        print(self.kwargs['recipe_id'])
        return Favorite.objects.get(
            user=self.request.user,
            recipe=favorites,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return super(FavoriteViewSet, self).destroy(request, *args, **kwargs)

    # не работает удаление
    """def destroy(self, request, pk=None):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        user = self.request.user
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        if not Favorite.objects.filter(recipe=recipe).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)"""


class SubscriptionViewSet(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = SubscriptionSerializer
    pagination_class = UserPagination
    permission_classes = [IsOwnerAdminModeratorOrReadOnly]
    http_method_names = ['get']

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)
