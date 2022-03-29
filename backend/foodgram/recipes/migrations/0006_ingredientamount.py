# Generated by Django 2.2.6 on 2022-03-29 04:22

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_shoppingcart'),
    ]

    operations = [
        migrations.CreateModel(
            name='IngredientAmount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1, message='Количество не менее 1'), django.core.validators.MaxValueValidator(100000, message='Количество не более 100000')], verbose_name='Количество')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient_amount', to='recipes.Ingredient', verbose_name='Ингредиент')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_amount', to='recipes.Recipe', verbose_name='Рецепт')),
            ],
        ),
    ]