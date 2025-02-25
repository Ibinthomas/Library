from django.contrib import admin
from .models import *
from django.contrib import admin
from .models import Book, Rental

admin.site.register(Book)
admin.site.register(Category)
admin.site.register(Rental)

