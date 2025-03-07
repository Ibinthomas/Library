from django.urls import path
from . import views

urlpatterns=[
    path('',views.user_home),
    path('login',views.book_login),
    path('register/',views.register),
    path('logout',views.book_logout),
    # -------admin----------
    path('admin_home',views.admin_home),
    path('add_book',views.add_book),
    path('edit_book/<id>',views.edit_book),
    path('add_category',views.add_category),
    path('mng_book/', views.mng_book, name='mng_book'),
    path('view_cat/<id>',views.view_cat),
    path('delete_book/<id>',views.delete_book),
    path('delete_category/<id>',views.delete_category),
    path('update_rental_status/<int:rental_id>/<str:status>/', views.update_rental_status, name='update_rental_status'),

    # # ------user------------
    path('user_home/', views.user_home,),
    path('view_book/<id>',views.view_book),
    path('view_book/<int:id>/', views.view_book, name='view_book'),
    path('about',views.about),
    path('view_category/<id>',views.view_category),
    path('book_issue/<id>',views.book_issue),
    path('profile',views.user_profile),
    path('contact/', views.contact, name='contact'),
    path('search/', views.search_books, name='search_books'),



    # path("return/<int:rental_id>/",views.return_book,),
    # path("my-rentals/", views.user_rentals,),
]