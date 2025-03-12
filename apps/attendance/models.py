from django.db import models
from django.contrib.auth.models import User

class Stamps(models.Model):
    empid = models.CharField(max_length=255, blank=True, null=True)
    dateandtime = models.DateTimeField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    auth_result = models.CharField(max_length=255, blank=True, null=True)
    auth_type = models.CharField(max_length=255, blank=True, null=True)
    device_name = models.CharField(max_length=255, blank=True, null=True)
    device_serial = models.CharField(max_length=255, blank=True, null=True)
    reader_name = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    card_number = models.CharField(max_length=255, blank=True, null=True)
    direction = models.CharField(max_length=255, blank=True, null=True)
    attendance_status = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stamps'
    
def __str__(self):
    return f"ID: {self.id}, EmpID: {self.empid}, Date/Time: {self.dateandtime}, Status: {self.attendance_status}"

class ManualCheckout(models.Model):
    empid = models.CharField(max_length=255)
    checkout_time = models.DateTimeField()
    checkout_date = models.DateField()
    checkout_time_only = models.TimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Manual Checkout: {self.empid} at {self.checkout_time}"
    
    def save(self, *args, **kwargs):
        # Set the date and time fields if not already set
        if self.checkout_time and not self.checkout_date:
            self.checkout_date = self.checkout_time.date()
        if self.checkout_time and not self.checkout_time_only:
            self.checkout_time_only = self.checkout_time.time()
            
        # First save the ManualCheckout record
        super().save(*args, **kwargs)
        
        # Then create a new entry in the stamps table
        latest_checkin = Stamps.objects.filter(
            empid=self.empid,
            date=self.checkout_date,
            direction='entry',
            attendance_status='check-in'
        ).order_by('-dateandtime').first()
        
        if latest_checkin:
            # Create the checkout record
            checkout = Stamps(
                empid=self.empid,
                dateandtime=self.checkout_time,
                date=self.checkout_date,
                time=self.checkout_time_only,
                auth_result='success',
                auth_type='ManualCheckout',
                device_name=latest_checkin.device_name,
                device_serial=latest_checkin.device_serial,
                reader_name=latest_checkin.reader_name,
                first_name=latest_checkin.first_name,
                last_name=latest_checkin.last_name,
                full_name=latest_checkin.full_name,
                department=latest_checkin.department,
                card_number=latest_checkin.card_number,
                direction='exit',
                attendance_status='check-out'
            )
            checkout.save()
