from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

class Book(models.Model):
    name= models.CharField(max_length=200)
    price= models.DecimalField(max_digits=10,decimal_places=2)

    class Meta:
        verbose_name_plural = 'Books'

    def __str__(self):
        return self.name
    




pricing_plans = [
    ('Sapa Pricing', 'Sapa Pricing'),
    ('Baller Pricing', 'Baller Pricing'),
    ('9-5 Pricing', '9-5 Pricing')
]

class PricingPlan(models.Model):
    plans = models.CharField(max_length=100, choices=pricing_plans, null=True, blank=True)
    pricing = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def  __str__ (self):
        return self.plans



queries = (

    ('Pricing Query', "Pricing Query"),
    ('Author Query', "Author Query"),
    ('Content Query', "Content Query"),
    ('Other Query', "Other Query")
)


class Get_in_touch(models.Model):

    email = models.CharField(max_length=200,blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    customer_query= models.CharField(choices=queries,default='Pricing Query',max_length=200)
    body = models.TextField(max_length=200, blank=True, null=True)
    
    
    
    class Meta:
        verbose_name_plural = 'Get in touch objects'

    def __str__(self):
        return f'queries by {self.name}'