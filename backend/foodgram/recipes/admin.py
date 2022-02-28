from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, Tag


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'amount', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug', 'color')
    search_fields = ('name',)
    list_filter = ('slug',)
    empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'name', 'author', 'text', 'created', 'count_favorite',
        'cooking_time', 'get_tags', 'get_ingredients', 'image'
    )
    search_fields = ('text',)
    list_filter = ('name', 'author', 'tags',)
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user', 'recipe',)
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
