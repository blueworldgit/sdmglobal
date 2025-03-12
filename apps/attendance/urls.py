from django.urls import path
from . import views

urlpatterns = [
    #path('hello/', views.hello_world, name='hello_world'),
   
    path('drill/', views.firedrill, name='firedrill'),
    path('missing-checkouts/', views.missing_checkouts, name='missing_checkouts'),
    path('manual-checkout/<str:empid>/<str:date>/', views.create_manual_checkout, name='create_manual_checkout'),
    
   
]