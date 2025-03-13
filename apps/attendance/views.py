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
    # Get start and end dates from request
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    # Default to today if no dates provided
    today = timezone.now().date()
    
    # Process start date
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            start_date = today
    else:
        start_date = today
    
    # Process end date
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            end_date = today
    else:
        end_date = today
    
    # Ensure end_date is not before start_date
    if end_date < start_date:
        end_date = start_date
    
    # Enforce maximum 7-day range
    max_range = timedelta(days=7)
    if end_date - start_date > max_range:
        end_date = start_date + max_range
        messages.warning(request, "Date range has been limited to 7 days maximum.")
    
    # Get all check-ins for the date range
    checkins = Stamps.objects.filter(
        date__gte=start_date,
        date__lte=end_date,
        direction='entry',
        attendance_status='check-in'
    ).values('empid', 'full_name', 'department', 'dateandtime', 'date')
    
    # Organize results by date and employee
    missing_by_date = {}
    
    for checkin in checkins:
        # Get checkouts for this employee on the same day
        date_str = checkin['date'].strftime('%Y-%m-%d')
        has_checkout = Stamps.objects.filter(
            empid=checkin['empid'],
            date=checkin['date'],
            direction='exit',
            attendance_status='check-out'
        ).exists()
        
        if not has_checkout:
            # Store by date for easy displaying
            if date_str not in missing_by_date:
                missing_by_date[date_str] = {
                    'date_obj': checkin['date'],
                    'formatted_date': checkin['date'].strftime('%A, %B %d, %Y'),
                    'missing': []
                }
            
            missing_by_date[date_str]['missing'].append(checkin)
    
    # Sort dates for display
    sorted_dates = sorted(missing_by_date.keys())
    missing_results = [missing_by_date[date] for date in sorted_dates]
    
    context = {
        'missing_results': missing_results,
        'start_date': start_date,
        'end_date': end_date,
        'title': 'Missing Checkouts',
    }
    return render(request, 'attendance/missing_checkouts.html', context)

@login_required
def create_manual_checkout(request, empid, date):
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, "Invalid date format.")
        return redirect(reverse('missing_checkouts'))

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

            # Correct redirect with query parameters
            start_date = request.GET.get('start_date', date)
            end_date = request.GET.get('end_date', date)
            return redirect(reverse('missing_checkouts') + f'?start_date={start_date}&end_date={end_date}')
    
    else:
        default_time = datetime.combine(date_obj, time(17, 0))  # 5:00 PM
        form = ManualCheckoutForm(initial={'checkout_time': default_time})

    context = {
        'form': form,
        'employee': checkin,
        'date': date_obj,
        'title': 'Create Manual Checkout',
    }
    return render(request, 'attendance/manual_checkout_form.html', context)


