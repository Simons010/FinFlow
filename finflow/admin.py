from django.contrib import admin
from .models import Category, Transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_type', 'user', 'created_at')
    list_filter = ('category_type', 'created_at')
    search_fields = ('name', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Category Info', {
            'fields': ('user', 'name', 'category_type')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('description', 'transaction_type', 'amount', 'category', 'date', 'user')
    list_filter = ('transaction_type', 'date', 'category')
    search_fields = ('description', 'user__username')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Transaction Info', {
            'fields': ('user', 'date', 'description', 'category', 'transaction_type', 'amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

