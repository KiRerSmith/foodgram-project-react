from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('users', views.UserViewSet, basename='userviewset')
router.register(r'recipes', views.RecipeViewSet, basename='recipes')
router.register(r'tags', views.TagViewSet, basename='tags')
router.register(
    r'ingredients',
    views.IngredientViewSet,
    basename='ingredients')
router.register(
    r'users/subscriptions',
    views.SubscriptionViewSet,
    basename='subscriptions')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls.jwt')),
    path('', include(router.urls)),
]
