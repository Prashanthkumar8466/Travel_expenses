from django.contrib import admin

from .models import Category,Expense
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id']

@admin.register(Expense)
class ExpensesAdmin(admin.ModelAdmin):
    list_display = ['id']
