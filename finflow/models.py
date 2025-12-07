from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from datetime import date

class Category(models.Model):
    """Transaction category model"""
    CATEGORY_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'name', 'category_type')
        verbose_name_plural = 'Categories'
        ordering = ['category_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"
    
    @property
    def transaction_count(self):
        """Get count of transactions in this category"""
        return self.transactions.count()
 

class Transaction(models.Model):
    """Financial transaction model"""
    TRANSACTION_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateField(default=date.today)
    description = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', '-date']),
            models.Index(fields=['user', 'transaction_type']),
            models.Index(fields=['user', 'category']),
        ]
    
    def __str__(self):
        return f"{self.description} - {self.amount} ({self.get_transaction_type_display()})"

