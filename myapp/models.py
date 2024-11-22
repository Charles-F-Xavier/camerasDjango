from django.db import models

# Create your models here.

class Count(models.Model):
    id = models.CharField(max_length=36, primary_key=True)  # ID como Char(36)
    device_id = models.CharField(max_length=255)  # device_id como Varchar(255)
    quantity = models.IntegerField()  # quantity como Int(11)
    camera_id = models.CharField(max_length=255)  # camera_id como Varchar(255)
    date = models.DateTimeField()  # date como Timestamp

    def __str__(self):
        txt= "{0} | Device {1} | Camera {2} | Quantity {3} | Date {4}"
        return txt.format(self.id,self.device_id,self.quantity,self.camera_id,self.date)
