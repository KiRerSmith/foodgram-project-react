from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User


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
        blank=False, null=True,
        verbose_name='Картинка'
    )
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        through_fields=('recipe', 'ingredient'),
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
        return self.name

    def get_ingredients(self):
        return "\n".join([i.name for i in self.ingredients.all()])

    def get_tags(self):
        return "\n".join([i.name for i in self.tags.all()])

    def count_favorite(self):
        return Favorite.objects.filter(recipe=self.pk).count()


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='ingredient_amount',
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe_amount',
        verbose_name='Рецепт'
    )
    amount = models.IntegerField(verbose_name='Количество', default=1,
                                 validators=[
                                    MinValueValidator(
                                        1,
                                        message='Количество не менее 1'
                                    ),
                                    MaxValueValidator(
                                        100000,
                                        message='Количество не более 100000'
                                    ),
                                 ])

    class Meta:
        ordering = ['pk']
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Объекты количества ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient'
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='cook',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ['pk']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='buyer',
        verbose_name='Покупатель'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='shoppingrecipe',
        verbose_name='Рецепт для покупок'
    )

    class Meta:
        ordering = ['pk']
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
