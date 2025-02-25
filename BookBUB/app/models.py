from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, date



class Category(models.Model):
    category= models.TextField()

class Book(models.Model):
    
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=50)
    image = models.FileField()
    dis=models.TextField()
    publication_date = models.DateField()
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    available_copies = models.PositiveIntegerField(default=1)
    def __str__(self):
        return self.name
    
    

class Rental(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateField()
    return_date = models.DateField()
    due_date = models.DateField()
    num_days = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    is_returned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.book.name}"