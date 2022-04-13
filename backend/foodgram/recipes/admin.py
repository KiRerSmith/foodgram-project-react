from django.contrib import admin

from .forms import RecipeIngredientForm
from .models import (Favorite, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Tag)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug', 'color')
    search_fields = ('name',)
    list_filter = ('slug',)
    empty_value_display = '-пусто-'


class RecipeIngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    formset = RecipeIngredientForm
    extra = 0
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = (
        'pk', 'name', 'author', 'text', 'created', 'count_favorite',
        'cooking_time', 'get_tags', 'get_ingredients', 'image'
    )
    readonly_fields = ('favorite_count',)
    search_fields = ('text',)
    list_filter = ('name', 'author', 'tags',)
    empty_value_display = '-пусто-'

    def favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj.pk).count()

    favorite_count.short_description = 'Количество избранных'


class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('pk', 'ingredient', 'amount', 'recipe')
    search_fields = ('ingredient',)
    list_filter = ('ingredient',)
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user', 'recipe',)
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user', 'recipe',)
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
