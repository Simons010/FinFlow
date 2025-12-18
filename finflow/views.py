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
    
    now = datetime.now()
    hour = now.hour
    
    # Determine greeting and gradient
    if hour < 12:
        greeting = "Good morning"
        gradient_class = "bg-gradient-to-r from-blue-900 to-blue-300"
    elif hour < 17:
        greeting = "Good afternoon"
        gradient_class = "bg-gradient-to-r from-yellow-900 to-yellow-300"
    else:
        greeting = "Good evening"
        gradient_class = "bg-gradient-to-r from-purple-900 to-purple-300"
    
    # Calculate statistics
    total_income = transactions.filter(transaction_type='income').aggregate(
        total=models.Sum('amount'))['total'] or Decimal('0')
    total_expenses = transactions.filter(transaction_type='expense').aggregate(
        total=models.Sum('amount'))['total'] or Decimal('0')
    net_profit = total_income - total_expenses
    profit_margin = (net_profit / total_income * 100) if total_income > 0 else Decimal('0')
    
    # Recent transactions
    recent_transactions = transactions[:10]
    
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
        'greeting' : greeting,
        'gradient_class': gradient_class,
        'now': now,
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
    user = request.user
    transactions = Transaction.objects.filter(user=user)

    # -----------------------------
    # TOTAL INCOME & EXPENSES
    # -----------------------------
    total_income = transactions.filter(transaction_type='income').aggregate(
        total=models.Sum('amount')
    )['total'] or Decimal('0')

    total_expenses = transactions.filter(transaction_type='expense').aggregate(
        total=models.Sum('amount')
    )['total'] or Decimal('0')

    net_profit = total_income - total_expenses

    # -----------------------------
    # LAST MONTH VS THIS MONTH COMPARISONS
    # -----------------------------
    today = datetime.today()
    first_day_this_month = today.replace(day=1)
    last_month_end = first_day_this_month - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    # This month totals
    income_this_month = transactions.filter(
        transaction_type='income',
        date__gte=first_day_this_month
    ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

    expenses_this_month = transactions.filter(
        transaction_type='expense',
        date__gte=first_day_this_month
    ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

    profit_this_month = income_this_month - expenses_this_month

    # Last month totals
    income_last_month = transactions.filter(
        transaction_type='income',
        date__range=[last_month_start, last_month_end]
    ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

    expenses_last_month = transactions.filter(
        transaction_type='expense',
        date__range=[last_month_start, last_month_end]
    ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

    profit_last_month = income_last_month - expenses_last_month

    # Percentage change helpers
    def percent_change(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100, 2)

    income_change_percent = percent_change(income_this_month, income_last_month)
    expense_change_percent = percent_change(expenses_this_month, expenses_last_month)
    net_profit_change = percent_change(profit_this_month, profit_last_month)

    # Profit margin
    profit_margin = (
        round((float(net_profit) / float(total_income)) * 100, 2)
        if total_income > 0 else 0
    )

    # -----------------------------
    # TOP INCOME + EXPENSE CATEGORIES
    # -----------------------------
    income_categories = []
    for cat in Category.objects.filter(user=user, category_type='income'):
        amount = transactions.filter(category=cat).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0')

        income_categories.append({"name": cat.name, "amount": float(amount)})

    top_income_category = (
        max(income_categories, key=lambda x: x["amount"])["name"]
        if income_categories else "None"
    )

    expense_categories_data = []
    for cat in Category.objects.filter(user=user, category_type='expense'):
        amount = transactions.filter(category=cat).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0')

        expense_categories_data.append({"name": cat.name, "amount": float(amount)})

    top_expense_category = (
        max(expense_categories_data, key=lambda x: x["amount"])["name"]
        if expense_categories_data else "None"
    )

    # TRANSACTION COUNTS
    income_transactions = transactions.filter(transaction_type='income').count()
    expense_transactions = transactions.filter(transaction_type='expense').count()

    monthly_data = []
    today = datetime.today().replace(day=1)

    for i in range(6):
        month_start = (today - timedelta(days=30 * i)).replace(day=1)
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        month_end = next_month - timedelta(days=1)

        m_income = transactions.filter(
            transaction_type="income",
            date__range=[month_start, month_end]
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

        m_expenses = transactions.filter(
            transaction_type="expense",
            date__range=[month_start, month_end]
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

        monthly_data.append({
            "month": month_start.strftime("%b %Y"),
            "income": float(m_income),
            "expenses": float(m_expenses),
            "net_profit": float(m_income - m_expenses),
        })

    monthly_data.reverse()

    # Expense categories for doughnut
    expense_categories = expense_categories_data

    # Top income sources (bar chart)
    top_income_sources = sorted(income_categories, key=lambda x: x['amount'], reverse=True)[:5]

    context = {
        # Cards
        "total_income": float(total_income),
        "total_expenses": float(total_expenses),
        "net_profit": float(net_profit),

        "income_change_percent": income_change_percent,
        "expense_change_percent": expense_change_percent,
        "net_profit_change": net_profit_change,
        "profit_margin": profit_margin,

        "top_income_category": top_income_category,
        "top_expense_category": top_expense_category,

        "income_transactions": income_transactions,
        "expense_transactions": expense_transactions,

        # Charts
        "monthly_data": monthly_data,
        "expense_categories": expense_categories,
        "top_income_sources": top_income_sources,
    }

    return render(request, "finflow/reports.html", context)




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
def update_transaction(request, pk):
    """Update an existing transaction"""
    user = request.user
    transaction = get_object_or_404(Transaction, id=pk, user=user)

    try:
        date = request.POST.get('date')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        transaction_type = request.POST.get('type')
        amount = request.POST.get('amount')

        category = get_object_or_404(Category, id=category_id, user=user)

        transaction.date = date
        transaction.description = description
        transaction.category = category
        transaction.transaction_type = transaction_type
        transaction.amount = Decimal(amount)
        transaction.save()

        messages.success(request, 'Transaction updated successfully.')
    except Exception as e:
        messages.error(request, f'Error updating transaction: {str(e)}')

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
    is_ajax = request.POST.get('ajax') == 'true'
    
    try:
        category = Category.objects.create(
            user=user,
            name=name,
            category_type=category_type
        )
        message = f'Category "{name}" added successfully.'
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': message,
                'category': {
                    'id': category.id,
                    'name': category.name,
                    'type': category.category_type,
                    'transaction_count': category.transaction_count
                }
            })
        else:
            messages.success(request, message)
    except Exception as e:
        error_msg = f'Error creating category: {str(e)}'
        if is_ajax:
            return JsonResponse({'success': False, 'message': error_msg}, status=400)
        else:
            messages.error(request, error_msg)
    
    return redirect('finflow:categories')


@login_required
@require_http_methods(["POST"])
def delete_category(request, pk):
    """Delete a category"""
    category = get_object_or_404(Category, id=pk, user=request.user)
    category_name = category.name
    is_ajax = request.POST.get('ajax') == 'true'
    
    try:
        category.delete()
        message = f'Category "{category_name}" deleted successfully.'
        if is_ajax:
            return JsonResponse({'success': True, 'message': message, 'id': pk})
        else:
            messages.success(request, message)
    except Exception as e:
        error_msg = f'Error deleting category: {str(e)}'
        if is_ajax:
            return JsonResponse({'success': False, 'message': error_msg}, status=400)
        else:
            messages.error(request, error_msg)
    
    return redirect('finflow:categories')



@login_required
@require_http_methods(["POST"])
def update_category(request, pk):
    """Update an existing category"""
    user = request.user
    category = get_object_or_404(Category, id=pk, user=user)

    name = request.POST.get('name')
    category_type = request.POST.get('category_type', category.category_type)
    is_ajax = request.POST.get('ajax') == 'true'

    try:
        category.name = name
        category.category_type = category_type
        category.save()
        message = f'Category "{name}" updated successfully.'
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': message,
                'category': {
                    'id': category.id,
                    'name': category.name,
                    'type': category.category_type,
                    'transaction_count': category.transaction_count
                }
            })
        else:
            messages.success(request, message)
    except Exception as e:
        error_msg = f'Error updating category: {str(e)}'
        if is_ajax:
            return JsonResponse({'success': False, 'message': error_msg}, status=400)
        else:
            messages.error(request, error_msg)

    return redirect('finflow:categories')


