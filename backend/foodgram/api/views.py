# from urllib import request
from functools import partial
from msilib.schema import CreateFolder
from turtle import update
from venv import create
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
from .serializers import (IngredientSerializer, RecipeSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserSerializer)
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


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination
    # (IsAdmin,)
    permission_classes = [IsOwnerAdminModeratorOrReadOnly]
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
        return UserSerializer

    @action(detail=False)
    def me(self, request):
        request_user = request.user
        queryset = User.objects.filter(id=request_user.id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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
    serializer_class = RecipeSerializer
    pagination_class = UserPagination
    permission_classes = [IsOwnerAdminModeratorOrReadOnly]
    filter_backends = (DjangoFilterBackend, )

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    """def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CreateRecipeSerializer
        return RetriveRecipeSerializer"""


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

# неправильно работает
class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = SubscriptionSerializer
    pagination_class = UserPagination
    permission_classes = [IsOwnerAdminModeratorOrReadOnly]
