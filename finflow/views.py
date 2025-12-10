from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db import models
from datetime import datetime, timedelta
from decimal import Decimal
from .models import Transaction, Category, Profile
import csv
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

@login_required
def dashboard(request):
    """Dashboard view with financial overview"""
    user = request.user
    transactions = Transaction.objects.filter(user=user)
    
    # Calculate statistics
    total_income = transactions.filter(transaction_type='income').aggregate(
        total=models.Sum('amount'))['total'] or Decimal('0')
    total_expenses = transactions.filter(transaction_type='expense').aggregate(
        total=models.Sum('amount'))['total'] or Decimal('0')
    net_profit = total_income - total_expenses
    profit_margin = (net_profit / total_income * 100) if total_income > 0 else Decimal('0')
    
    # Recent transactions
    recent_transactions = transactions[:5]
    
    # Monthly data for charts
    today = datetime.today()
    monthly_data = []
    for i in range(6):
        month_start = today.replace(day=1) - timedelta(days=30*i)
        month_start = month_start.replace(day=1)
        if i == 0:
            month_end = today
        else:
            month_end = month_start + timedelta(days=32)
            month_end = month_end.replace(day=1) - timedelta(days=1)
        
        month_income = transactions.filter(
            transaction_type='income',
            date__range=[month_start, month_end]
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        
        month_expenses = transactions.filter(
            transaction_type='expense',
            date__range=[month_start, month_end]
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'income': float(month_income),
            'expenses': float(month_expenses),
        })
    
    monthly_data.reverse()
    
    context = {
        'total_income': float(total_income),
        'total_expenses': float(total_expenses),
        'net_profit': float(net_profit),
        'profit_margin': float(profit_margin),
        'recent_transactions': recent_transactions,
        'monthly_data': monthly_data,
    }
    
    return render(request, 'finflow/dashboard.html', context)


@login_required
def transactions(request):
    """Transactions management view"""
    user = request.user
    transactions = Transaction.objects.filter(user=user)
    categories = Category.objects.filter(user=user)
    
    # Filters
    search = request.GET.get('search', '')
    transaction_type = request.GET.get('type', '')
    category_id = request.GET.get('category', '')
    
    if search:
        transactions = transactions.filter(description__icontains=search)
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    
    context = {
        'transactions': transactions,
        'categories': categories,
        'search': search,
        'selected_type': transaction_type,
        'selected_category': category_id,
    }
    
    return render(request, 'finflow/transactions.html', context)


@login_required
def categories(request):
    """Categories management view"""
    user = request.user
    income_categories = Category.objects.filter(user=user, category_type='income')
    expense_categories = Category.objects.filter(user=user, category_type='expense')
    
    context = {
        'income_categories': income_categories,
        'expense_categories': expense_categories,
    }
    
    return render(request, 'finflow/categories.html', context)


@login_required
def reports(request):
    """Financial reports view"""
    user = request.user
    transactions = Transaction.objects.filter(user=user)
    
    # P&L Statement
    total_income = transactions.filter(transaction_type='income').aggregate(
        total=models.Sum('amount'))['total'] or Decimal('0')
    total_expenses = transactions.filter(transaction_type='expense').aggregate(
        total=models.Sum('amount'))['total'] or Decimal('0')
    net_profit = total_income - total_expenses
    
    # Monthly breakdown (last 6 months)
    today = datetime.today()
    monthly_data = []
    for i in range(6):
        month_start = today.replace(day=1) - timedelta(days=30*i)
        month_start = month_start.replace(day=1)
        if i == 0:
            month_end = today
        else:
            month_end = month_start + timedelta(days=32)
            month_end = month_end.replace(day=1) - timedelta(days=1)
        
        month_income = transactions.filter(
            transaction_type='income',
            date__range=[month_start, month_end]
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        
        month_expenses = transactions.filter(
            transaction_type='expense',
            date__range=[month_start, month_end]
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'income': float(month_income),
            'expenses': float(month_expenses),
            'net_profit': float(month_income - month_expenses),
        })
    
    monthly_data.reverse()
    
    # Expense categories (for doughnut chart)
    expenses_by_category = []
    for category in Category.objects.filter(user=user, category_type='expense'):
        total = transactions.filter(category=category).aggregate(
            total=models.Sum('amount'))['total'] or Decimal('0')
        expenses_by_category.append({
            'name': category.name,
            'amount': float(total),
        })
    
    # Top 5 income sources (bar chart)
    income_categories = []
    for category in Category.objects.filter(user=user, category_type='income'):
        total = transactions.filter(category=category).aggregate(
            total=models.Sum('amount'))['total'] or Decimal('0')
        income_categories.append({
            'name': category.name,
            'amount': float(total),
        })
    top_income_sources = sorted(income_categories, key=lambda x: x['amount'], reverse=True)[:5]
    
    context = {
        'total_income': float(total_income),
        'total_expenses': float(total_expenses),
        'net_profit': float(net_profit),
        'monthly_data': monthly_data,
        'expense_categories': expenses_by_category,
        'top_income_sources': top_income_sources,
    }
    
    return render(request, 'finflow/reports.html', context)



@login_required
def settings(request):
    """Settings view"""
    user = request.user
    profile = user.profile
    
    # Ensure profile exists
    profile, created = Profile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        # Handle settings update
        
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        
        user.save()
        
        profile.business_name = request.POST.get('business_name', '')
        profile.current_year = datetime.now().year
        
        if 'business_logo' in request.FILES:
            profile.business_logo = request.FILES['business_logo']
            
        profile.save()
            
        messages.success(request, 'Settings updated successfully.')
        return redirect('finflow:settings') 
    
    context = {
        'user': user,
        'profile': profile,
    }
    
    return render(request, 'finflow/settings.html', context)

#export csv view
def export_report_csv(request):
    # Calculate totals
    total_income = Transaction.objects.filter(
        user=request.user,
        transaction_type='income'
    ).aggregate(total=models.Sum('amount'))['total'] or 0

    total_expenses = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense'
    ).aggregate(total=models.Sum('amount'))['total'] or 0

    net_profit = total_income - total_expenses

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        f'attachment; filename="finflow_report_{datetime.now().strftime("%Y%m%d")}.csv"'
    )
    
    writer = csv.writer(response)

    # Header
    writer.writerow(['FinFlow - Financial Report'])
    writer.writerow([f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}'])
    writer.writerow([])
    
    # P&L Summary
    writer.writerow(['Profit & Loss Statement'])
    writer.writerow(['Total Income', f'Ksh {total_income}'])
    writer.writerow(['Total Expenses', f'Ksh {total_expenses}'])
    writer.writerow(['Net Profit', f'Ksh {net_profit}'])
    writer.writerow([])
    
    # All Transactions
    writer.writerow(['All Transactions'])
    writer.writerow(['Date', 'Description', 'Category', 'Type', 'Amount'])
    
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    
    for t in transactions:
        writer.writerow([
            t.date,
            t.description,
            t.category.name if t.category else '',
            t.transaction_type.title(),
            f'Ksh {t.amount}'
        ])
    
    return response

#export excel view
def export_report_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "FinFlow Report"

    # Create data
    transactions = Transaction.objects.filter(user=request.user)

    ws.append(["Date", "Description", "Category", "Type", "Amount"])

    for t in transactions:
        ws.append([
            t.date,
            t.description,
            t.category.name if t.category else "",
            t.transaction_type.title(),
            t.amount
        ])

    # Prepare response
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="finflow_report_{datetime.now().strftime("%Y%m%d")}.xlsx"'
    )

    wb.save(response)
    return response

#export pdf view
def export_report_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="finflow_report_{datetime.now().strftime("%Y%m%d")}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    y = height - 50
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "FinFlow - Financial Report")

    y -= 40
    p.setFont("Helvetica", 12)

    transactions = Transaction.objects.filter(user=request.user)

    for t in transactions:
        p.drawString(50, y, f"{t.date} - {t.description} - {t.category} - {t.transaction_type} - Ksh {t.amount}")
        y -= 18

        if y < 50:
            p.showPage()
            p.setFont("Helvetica", 12)
            y = height - 50

    p.save()
    return response


# API endpoints for AJAX requests

@login_required
@require_http_methods(["POST"])
def add_transaction(request):
    """Add a new transaction via AJAX"""
    try:
        user = request.user
        date = request.POST.get('date')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        transaction_type = request.POST.get('type')
        amount = request.POST.get('amount')
        
        category = get_object_or_404(Category, id=category_id, user=user)
        
        transaction = Transaction.objects.create(
            user=user,
            date=date,
            description=description,
            category=category,
            transaction_type=transaction_type,
            amount=Decimal(amount)
        )
        messages.success(request, "Transaction added successfully. ")
        JsonResponse({'success': True, 'message': 'Transaction added successfully.'})
    except Exception as e:
        messages.error(request, f"Error creating transaction {str(e)}")
        JsonResponse({'success': False, 'message': str(e)}, status=400)
        
    return redirect('finflow:transactions')


@login_required
@require_http_methods(["POST"])
def delete_transaction(request, pk):
    """Delete a transaction"""
    transaction = get_object_or_404(Transaction, id=pk, user=request.user)
    transaction.delete()
    messages.success(request, 'Transaction deleted successfully.')
    return redirect('finflow:transactions')


@login_required
@require_http_methods(["POST"])
def add_category(request):
    """Add a new category"""
    user = request.user
    name = request.POST.get('name')
    category_type = request.POST.get('category_type')
    
    try:
        Category.objects.create(
            user=user,
            name=name,
            category_type=category_type
        )
        messages.success(request, f'Category "{name}" added successfully.')
    except Exception as e:
        messages.error(request, f'Error creating category: {str(e)}')
    
    return redirect('finflow:categories')


@login_required
@require_http_methods(["POST"])
def delete_category(request, pk):
    """Delete a category"""
    category = get_object_or_404(Category, id=pk, user=request.user)
    category_name = category.name
    category.delete()
    messages.success(request, f'Category "{category_name}" deleted successfully.')
    return redirect('finflow:categories')


