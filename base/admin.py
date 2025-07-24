from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Book)
# admin.site.register(Review)




@admin.register(Get_in_touch)
class Get_in_touch(admin.ModelAdmin):
    list_display = ('name', 'email', 'body','customer_query')



@admin.register(PricingPlan)
class PricingPlan(admin.ModelAdmin):
    list_display = ('plans','pricing')


