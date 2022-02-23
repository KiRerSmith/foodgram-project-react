from django.contrib import admin

from .models import Ingredient, Recipe, Tag


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'amount', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug', 'color')
    search_fields = ('name',)
    list_filter = ('slug',)
    empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'author', 'text', 'created',
        'cooking_time', 'get_tags', 'get_ingredients', 'image'
    )
    search_fields = ('text',)
    list_filter = ('created', 'author',)
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
