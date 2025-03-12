from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import connection
from .models import Stamps, ManualCheckout
from datetime import datetime, timedelta, time
from .forms import ManualCheckoutForm
import pprint
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

def home_view(request):
    context = {'segment': 'index'}
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))
   

def firedrill(request):
        # Define the date filter
    date_time_filter = datetime.now() - timedelta(days=1)    
    formatted_date = date_time_filter.strftime("%Y-%m-%dT%H:%M:%S")
    
    # Define your raw SQL query
    query = """
    SELECT * 
    FROM stamps 
    WHERE dateandtime > %s 
    ORDER BY id;
"""
    latest_status = {}
    
    # Execute the query and fetch data
    with connection.cursor() as cursor:
        cursor.execute(query, [date_time_filter])
        stamps = cursor.fetchall()

       
    
    # Get the latest status for each employee
    
    for record in stamps:
        emp_id = record[1]  # Assuming empid is in column 1
        attendance_status = record[16]  # Assuming attendance_status is in column 2
        latest_status[emp_id] = record

    #pprint.pprint(stamps)
    #print(attendance_status)
    
    
    # Filter employees still in the building
    still_in_building = []
    for record in latest_status.values():
     if record[16] == "check-in": 
        still_in_building.append(record)
        
    
    pprint.pprint(still_in_building)
    # Pass data to the template
    #return render(request, 'home/map.html')
    return render(request, 'attendance/drill.html', {'employees': still_in_building})

@login_required
def missing_checkouts(request):
    # Get date from request or use today's date
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()
    
    # Get all check-ins for the selected date
    checkins = Stamps.objects.filter(
        date=selected_date,
        direction='entry',
        attendance_status='check-in'
    ).values('empid', 'full_name', 'department', 'dateandtime')
    
    # Get all check-outs for the selected date
    checkouts = Stamps.objects.filter(
        date=selected_date,
        direction='exit',
        attendance_status='check-out'
    ).values_list('empid', flat=True)
    
    # Find employees who checked in but didn't check out
    missing_checkouts = []
    for checkin in checkins:
        if checkin['empid'] not in checkouts:
            missing_checkouts.append(checkin)
    
    context = {
        'missing_checkouts': missing_checkouts,
        'selected_date': selected_date,
        'title': 'Missing Checkouts',
    }
    return render(request, 'attendance/missing_checkouts.html', context)

@login_required
def create_manual_checkout(request, empid, date):
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, "Invalid date format.")
        return redirect('missing_checkouts')
    
    # Get the latest check-in for this employee on this date
    checkin = get_object_or_404(Stamps, 
        empid=empid,
        date=date_obj,
        direction='entry',
        attendance_status='check-in'
    )
    
    if request.method == 'POST':
        form = ManualCheckoutForm(request.POST)
        if form.is_valid():
            manual_checkout = form.save(commit=False)
            manual_checkout.empid = empid
            manual_checkout.checkout_date = date_obj
            manual_checkout.checkout_time_only = form.cleaned_data['checkout_time'].time()
            manual_checkout.created_by = request.user
            manual_checkout.save()
            
            messages.success(request, f"Manual checkout created for {checkin.full_name}")
            return redirect('missing_checkouts')
    else:
        # Default time is end of workday (e.g., 5:00 PM)
       default_time = datetime.combine(date_obj, time(17, 0))  # 5:00 PM
       form = ManualCheckoutForm(initial={'checkout_time': default_time})
    
    context = {
        'form': form,
        'employee': checkin,
        'date': date_obj,
        'title': 'Create Manual Checkout',
    }
    return render(request, 'attendance/manual_checkout_form.html', context)



