# from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

"""import sys
sys.path.append('/foodgram/users/models')
import User"""
from users.models import User

# User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True, blank=False, null=True,
        verbose_name='Название')
    color = models.CharField(
        max_length=7,
        unique=True, blank=False, null=True,
        verbose_name='Цвет',
        default='#000000'
    )
    slug = models.SlugField(max_length=200, unique=True, default='')

    class Meta:
        ordering = ['pk']
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100,
        blank=False, null=True,
        verbose_name='Название')
    amount = models.IntegerField('Количество')
    measurement_unit = models.CharField(
        max_length=15,
        blank=False, null=True,
        verbose_name='Единицы измерения')

    class Meta:
        ordering = ['pk']
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=200,
        blank=False, null=True,
        verbose_name='Название')
    image = models.ImageField(
        upload_to='media/',
        blank=False, null=True,
        verbose_name='Картинка'
    )
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Тэги')
    cooking_time = models.IntegerField(
        'Время приготовления, мин',
        default=1,
        validators=[
            MinValueValidator(1)
        ]
    )
    created = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.text[:10]

    def get_ingredients(self):
        return "\n".join([i.name for i in self.ingredients.all()])

    def get_tags(self):
        return "\n".join([i.name for i in self.tags.all()])
