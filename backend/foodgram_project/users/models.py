from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Email',
        blank=False,
        null=False
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Логин',
        blank=False,
        null=False
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Имя',
        null=False,
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Фамилия',
        null=False
    )

    REQUIRED_FIELDS = (
        'email', 'first_name', 'last_name', 'password',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name='Автор рецепта',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author',),
                name='unique_subscription',
            ),
        )
        verbose_name = 'Список подписок'
        verbose_name_plural = 'Список подписок'
        ordering = ('author',)

    def __str__(self):
        return (f'Подписчик {self.user.username}) '
                f'автор {self.author.username}')
