from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True, blank=False, null=True,
        verbose_name='Название')
    color = models.CharField(
        max_length=7,
        unique=True, blank=False, null=True,
        verbose_name='Цвет',
        default='#000000'
    )
    slug = models.SlugField(unique=True, default='')

    class Meta:
        ordering = ['slug']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100,
        blank=False, null=True,
        verbose_name='Название')
    amount = models.IntegerField('Количество')
    unit = models.CharField(
        max_length=15,
        blank=False, null=True,
        verbose_name='Единицы измерения')

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=100,
        blank=False, null=True,
        verbose_name='Название')
    image = models.ImageField(
        upload_to='recipes/',
        blank=False, null=True,
        verbose_name='Картинка'
    )
    description = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты'
    )
    tag = models.ManyToManyField(Tag, verbose_name='Тэг')
    time = models.IntegerField('Время приготовления, мин')
    created = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.description[:10]
