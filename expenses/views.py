from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ( CreateView, DeleteView, DetailView, ListView, UpdateView )

from .forms import ExpenseFilterForm, ExpenseForm, RegisterForm
from .models import Expense


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('expense_list')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('expense_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Регистрация прошла успешно. Добро пожаловать!')
        return redirect(self.success_url)


class OwnerQuerysetMixin(LoginRequiredMixin):
    def get_queryset(self):
        return Expense.objects.filter(owner=self.request.user)


class ExpenseListView(OwnerQuerysetMixin, ListView):
    model = Expense
    template_name = 'expenses/expense_list.html'
    context_object_name = 'expenses'

    def get_queryset(self):
        qs = super().get_queryset()
        self.filter_form = ExpenseFilterForm(self.request.GET or None)

        if self.filter_form.is_valid():
            data = self.filter_form.cleaned_data
            if data['q']:
                qs = qs.filter(title__icontains=data['q'].strip())
            if data['category']:
                qs = qs.filter(category=data['category'])
            if data['payment_method']:
                qs = qs.filter(payment_method=data['payment_method'])
            if data['date_from']:
                qs = qs.filter(date__gte=data['date_from'])
            if data['date_to']:
                qs = qs.filter(date__lte=data['date_to'])
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.object_list
        context['total_count'] = qs.count()
        context['total_sum'] = qs.aggregate(total=Sum('amount'))['total'] or 0
        context['filter_form'] = self.filter_form
        context['filters_applied'] = any(
            self.request.GET.get(k)
            for k in ('q', 'category', 'payment_method', 'date_from', 'date_to')
        )
        return context


class ExpenseDetailView(OwnerQuerysetMixin, DetailView):
    model = Expense
    template_name = 'expenses/expense_detail.html'


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expense_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Расход успешно добавлен.')
        return super().form_valid(form)


class ExpenseUpdateView(OwnerQuerysetMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expense_list')

    def form_valid(self, form):
        messages.success(self.request, 'Расход успешно изменён.')
        return super().form_valid(form)


class ExpenseDeleteView(OwnerQuerysetMixin, DeleteView):
    model = Expense
    template_name = 'expenses/expense_confirm_delete.html'
    success_url = reverse_lazy('expense_list')

    def form_valid(self, form):
        messages.success(self.request, 'Расход успешно удалён.')
        return super().form_valid(form)