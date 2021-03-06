from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
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
router.register('users', views.UserViewSet, basename='userviewset')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls.jwt')),
    path('recipes/<int:recipe_id>/favorite/', views.favorite),
    path('users/<int:author_id>/subscribe/', views.subscribe),
    path('recipes/<int:recipe_id>/shopping_cart/', views.shopping_cart),
    path('recipes/download_shopping_cart/', views.download_shopping_cart),
    path('', include(router.urls)),
]
