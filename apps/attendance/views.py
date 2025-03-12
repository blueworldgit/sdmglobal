from django.shortcuts import render

from django.db import connection
from .models import Stamps
from datetime import datetime, timedelta
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



