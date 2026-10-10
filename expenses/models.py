from django.conf import settings
from django.db import models
from django.urls import reverse


class Expense(models.Model):
    class Category(models.TextChoices):
        FOOD = 'food', 'Продукты'
        TRANSPORT = 'transport', 'Транспорт'
        EDUCATION = 'education', 'Обучение'
        ENTERTAINMENT = 'entertainment', 'Развлечения'
        HEALTH = 'health', 'Здоровье'
        OTHER = 'other', 'Другое'

    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'Наличные'
        CARD = 'card', 'Карта'

    title = models.CharField('Название', max_length=200)
    amount = models.DecimalField('Сумма', max_digits=10, decimal_places=2)
    category = models.CharField(
        'Категория', max_length=20,
        choices=Category.choices, default=Category.OTHER,
    )
    payment_method = models.CharField(
        'Способ оплаты', max_length=10,
        choices=PaymentMethod.choices, default=PaymentMethod.CARD,
    )
    date = models.DateField('Дата расхода')
    comment = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expenses',
        verbose_name='Владелец',
    )

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Расход'
        verbose_name_plural = 'Расходы'

    def __str__(self):
        return f'{self.title} — {self.amount}'

    def get_absolute_url(self):
        return reverse('expense_detail', kwargs={'pk': self.pk})