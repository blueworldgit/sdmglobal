from django.db import models

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
