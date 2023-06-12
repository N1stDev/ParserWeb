from django.db import models


class ForumAuto(models.Model):
    Request = models.CharField(max_length=100, default="None")
    VendorCode = models.CharField(max_length=100, default="None")
    Brand = models.CharField(max_length=100, default="None")
    Product = models.CharField(max_length=100, default="None")
    Applicability = models.CharField(max_length=200, default="None")
    Returns = models.CharField(max_length=100, default="None")
    Delivery = models.CharField(max_length=100, default="None")
    Price = models.CharField(max_length=100, default="None")
    Stock = models.CharField(max_length=100, default="None")


class ShateM(models.Model):
    Request = models.CharField(max_length=100, default="None")
    Brand = models.CharField(max_length=100, default="None")
    Name = models.CharField(max_length=100, default="None")
    Stock = models.CharField(max_length=100, default="None")
    Amount = models.CharField(max_length=100, default="None")
    Rating = models.CharField(max_length=100, default="None")
    Delivery = models.CharField(max_length=100, default="None")
    Price = models.CharField(max_length=100, default="None")
