from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Expense


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'payment_method', 'date', 'comment']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if len(title) < 3:
            raise forms.ValidationError('Название должно содержать минимум 3 символа.')
        return title

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError('Сумма должна быть больше нуля.')
        return amount

    def clean_date(self):
        date = self.cleaned_data['date']
        if date > timezone.localdate():
            raise forms.ValidationError('Дата расхода не может быть в будущем.')
        return date


class ExpenseFilterForm(forms.Form):
    q = forms.CharField(required=False, label='Поиск по названию')
    category = forms.ChoiceField(
        required=False, label='Категория',
        choices=[('', 'Все категории')] + Expense.Category.choices,
    )
    payment_method = forms.ChoiceField(
        required=False, label='Способ оплаты',
        choices=[('', 'Любой способ')] + Expense.PaymentMethod.choices,
    )
    date_from = forms.DateField(
        required=False, label='С даты',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    date_to = forms.DateField(
        required=False, label='По дату',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    def clean(self):
        cleaned = super().clean()
        date_from = cleaned.get('date_from')
        date_to = cleaned.get('date_to')
        if date_from and date_to and date_from > date_to:
            self.add_error('date_to', 'Конечная дата не может быть раньше начальной.')
        return cleaned


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']