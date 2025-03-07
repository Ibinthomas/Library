from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from .models import *
import os
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib.auth.views import redirect_to_login
import re
from datetime import datetime, timedelta
from .models import Book, Rental, Category



# Create your views here.


def book_login(req):
    if 'admin' in req.session:
        # req.session.flush()
        return redirect(admin_home)
    else:
        if req.method=='POST':
            uname=req.POST['uname']
            password=req.POST['password']
            data=authenticate(username=uname,password=password)
            if data:
                login(req,data)
                if data.is_superuser:
                    req.session['admin']=uname     #create
                    return redirect(admin_home)
                else:
                    req.session['user']=uname
                    return redirect(user_home)
            else:
                messages.warning(req,'invalid username or password')
                return redirect(book_login)
    return render(req,'login.html')

def book_logout(req):
    logout(req)
    req.session.flush()
    return redirect(book_login)


def register(req):
    if req.method == 'POST':
        name = req.POST.get('name', '').strip()
        email = req.POST.get('email', '').strip()
        password = req.POST.get('password', '').strip()

        # Check for empty fields
        if not name or not email or not password:
            messages.error(req, "All fields are required.")
            return redirect(register)

        # Validate email format
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            messages.error(req, "Invalid email format.")
            return redirect(register)

        # Validate password strength (Minimum 8 characters, 1 digit, 1 letter, and 1 special character)
        if (
            len(password) < 8 
            or not re.search(r'\d', password) 
            or not re.search(r'[A-Za-z]', password) 
            or not re.search(r'[@$!%*?&]', password)  # Special characters check
        ):
            messages.error(req, "Password must be at least 8 characters long and include letters, numbers, and a special character (@, $, !, %, *, ?, &).")
            return redirect(register)

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.warning(req, 'User with this email already exists.')
            return redirect(register)

        # Create user
        try:
            user = User.objects.create_user(first_name=name, username=email, email=email, password=password)
            user.save()
            messages.success(req, "Registration successful! You can now log in.")
            return redirect(book_login)
        except Exception as e:
            messages.error(req, "An error occurred during registration. Please try again.")
            print(f"Error: {e}")  # Log error for debugging
            return redirect(register)

    return render(req, 'register.html')




    
# ______________________________admin________________________________


def admin_home(req):
    if 'admin' in req.session:
        book=Book.objects.all()
        return render(req,'admin/admin_home.html',{'books':book})
    else:
        return render(book_login)
    

def add_book(req):
    if 'admin' in req.session:
        if req.method=='POST':
            name=req.POST['name']
            author=req.POST['author']
            dis=req.POST['dis']
            publication_date= req.POST['publication_date']
            category=req.POST['category']
            status = req.POST.get('available_copies') == 'on'
            file=req.FILES['image']
            data=Book.objects.create(name=name,author=author,image=file,dis=dis,
                                    category=Category.objects.get(category=category),
                                    publication_date=publication_date,available_copies=status,
                                    )
            data.save()
        else:
            data=Category.objects.all()
            return render(req,'admin/add_book.html',{'data':data})
    return render(req,'admin/add_book.html')




def edit_book(req, id):
    book = get_object_or_404(Book, pk=id)  # Ensure book exists
    
    if req.method == 'POST':
        name = req.POST['name']
        author = req.POST['author']
        dis = req.POST['dis']
        publication_date = req.POST['publication_date']
        category_id = req.POST['category']  # Getting category as a string from form
        status = req.POST.get('available_copies') == 'on'
        file = req.FILES.get('image')

        # Ensure category_id is converted to an integer and fetch the actual Category instance
        # category = get_object_or_404(Category, pk=int(category_id))

        # Update the book
        book.name = name
        book.author = author
        book.dis = dis
        book.publication_date = publication_date
        # book.category = category
        book.available_copies = status

        if file:
            book.image = file  # Update image if a new file is uploaded

        book.save()  # Save changes

        return redirect(admin_home)

    else:
        data = Book.objects.get(pk=id)
        return render(req, 'admin/edit_book.html', {'data': data})


def add_category(req):
    if 'admin' in req.session:
        if req.method == 'POST':
            category=req.POST['category']
            data=Category.objects.create(category=category)
            data.save()
            return redirect(add_category)
        else:
            data=Category.objects.all()
            return render(req,'admin/add_category.html',{'data':data})

def view_cat(req,id):
    category = Category.objects.get(pk=id)
    book = Book.objects.filter(category=category)
    return render(req, 'admin/view_cat.html', {'category': category,'book': book})

def delete_category(req,id):
    data=Category.objects.get(pk=id)
    data.delete()
    return redirect(add_category)


def delete_book(req,id):
    data=Book.objects.get(pk=id)
    url=data.image.url
    url=url.split('/')[-1]
    os.remove('media/'+url)
    data.delete()
    return redirect(admin_home)

def mng_book(req):
    rentals = Rental.objects.all().order_by("-id")
    return render(req, "admin/mng_book.html", {"rentals": rentals})


def update_rental_status(request, rental_id, status):
    rental = get_object_or_404(Rental, id=rental_id)

    if status in ["Approved", "Rejected", "Returned"]:
        rental.status = status
        rental.save()
        
        subject = ""
        message = ""
        recipient_email = rental.user.email
        sender_email = settings.EMAIL_HOST_USER
        
        if status == "Approved":
            subject = "Your Book Issue Request Has Been Approved!"
            message = f"""
            Hello {rental.user.username},

            Your BookBUB request for '{rental.book.name}' has been approved.

            Start Date: {rental.issue_date}
            End Date: {rental.return_date}
            Due Date: {rental.due_date}

            Thank you for using our service!

            Best Regards,
            BookBUB Management Team
            """
        elif status == "Rejected":
            subject = "Your Book Issue Request Has Been Rejected"
            message = f"""
            Hello {rental.user.username},

            Sorry, your book rental request for '{rental.book.name}' has been rejected.

            Start Date: {rental.issue_date}
            End Date: {rental.return_date}
            Due Date: {rental.due_date}

            Thank you for using our service!

            Best Regards,
            Library Management Team
            """
        elif status == "Returned":
            subject = "Your Book Has Been Returned Successfully!"
            message = f"""
            Hello {rental.user.username},

            Your book '{rental.book.name}' has been successfully returned.

            Start Date: {rental.issue_date}
            End Date: {rental.return_date}
            Due Date: {rental.due_date}

            Thank you for using our service!

            Best Regards,
            BookBUB Management Team
            """
        
        send_mail(subject, message, sender_email, [recipient_email])
        messages.success(request, f"Rental status updated to {status}")
    else:
        messages.error(request, "Invalid status update")
    
    return redirect("mng_book")

# _______________________________User_________________________________

def user_home(req):
    if 'admin' in req.session:
        return redirect(admin_home)
    else:
        data=Book.objects.all()
        cat=Category.objects.all()
        return render(req,'user/user_home.html',{'data':data,'cat':cat})
    

def about(req):
    cat=Category.objects.all()
    return render(req,'user/about.html',{"cat":cat})

def search_books(request):
    cat=Category.objects.all()
    query = request.GET.get('q')
    books = Book.objects.filter(name__icontains=query) if query else []
    return render(request, 'user/search.html', {'books': books, 'query': query, 'cat':cat})


def contact(req):
    cat=Category.objects.all()
    if req.method == "POST":
        name = req.POST["name"]
        email = req.POST["email"]
        message = req.POST["message"]

        send_mail(
            subject=f"New Contact Form Submission from {name}",
            message=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
            from_email=email,
            recipient_list=["shozo1310@gmail.com"], 
            fail_silently=True,
        )

        messages.success(req, "Your message has been sent successfully!")
        return redirect(contact )  
    return render(req,'user/contact.html',{"cat":cat})

def view_book(req,id):
    data=Book.objects.get(pk=id)
    related_books = Book.objects.filter(category=data.category).exclude(id=data.id)  # Exclude the current book

    return render(req,'user/view_book.html',{'data':data,"relate": related_books})



def view_category(req,id):
    category = Category.objects.get(pk=id)
    cat=Category.objects.all()
    book = Book.objects.filter(category=category)
    return render(req, 'user/view_category.html', {'category': category,'book': book,"cat":cat})


@login_required
def book_issue(req, id):
    cat = Category.objects.all()
    book = get_object_or_404(Book, pk=id)

    if not book.available_copies:
        messages.error(req, "Sorry, this book is not available for rent.")
        return redirect('view_book', id=book.pk)

    if req.method == "POST":
        issue_date_str = req.POST.get("issue_date")
        return_date_str = req.POST.get("return_date")

        if issue_date_str and return_date_str:
            issue_date = datetime.strptime(issue_date_str, "%Y-%m-%d").date()
            return_date = datetime.strptime(return_date_str, "%Y-%m-%d").date()
            due_date = issue_date + timedelta(days=14)  # Default due date is 14 days after issue date

            if issue_date >= return_date:
                messages.error(req, "Return date must be after issue date.")
                return redirect('book_issue', id=book.pk)

            existing_rental = Rental.objects.filter(
                book=book,
                issue_date__lte=return_date,
                return_date__gte=issue_date,
                status__in=["Pending", "Approved"]
            ).exists()

            if existing_rental:
                messages.error(req, "This book is already booked for the selected dates.")
                return redirect('view_book', id=book.pk)

            num_days = (return_date - issue_date).days
            rental = Rental.objects.create(
                user=req.user,
                book=book,
                issue_date=issue_date,
                return_date=return_date,
                due_date=due_date,
                num_days=num_days,
                status="Pending"
            )

            messages.success(req, "Your rental request has been submitted successfully!")
            return redirect('view_book', id=book.pk)

    return render(req, "user/book_issue.html", {"book": book, "cat": cat})



def user_profile(req):
    cat=Category.objects.all()
    rentals = Rental.objects.filter(user=req.user).order_by("-id")
    return render(req,'user/user_profile.html',{'rentals':rentals,'cat':cat})



def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    related_books = book.related_books.all()  # Fetch related books
    return render(request, 'book_detail.html', {'book': book, 'related_books': related_books})

