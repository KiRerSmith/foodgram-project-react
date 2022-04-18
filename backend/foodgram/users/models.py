from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    admin = 'admin'
    user = 'user'
    CHOICES = (
        (admin, 'admin'),
        (user, 'user'),
    )

    username = models.CharField(
        unique=True, blank=False,
        max_length=150)
    # переопределение поля пароля, т.к. нужно 150 символов вместо 128
    password = models.CharField(blank=False, max_length=150)
    email = models.EmailField(
        unique=True, blank=False,
        max_length=254)
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    role = models.TextField(choices=CHOICES, default=user)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=['username', 'email'],
                                    name='uniq_signup'),
        )
        verbose_name = 'пользователя'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    @property
    def is_admin(self):
        return self.role == self.admin


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Блогер'
    )

    class Meta:
        ordering = ['pk']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_following'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='block_self_following'
            )
        ]
        verbose_name = 'подписку'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'Блогер-{self.author.username}->Подписчик-{self.user.username}'
