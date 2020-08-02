from django.urls import path

from . import views

urlpatterns = [
    path('', views.main_page),
    path('search/', views.search_page),
    path('course/', views.course_page),
    path('vote/', views.vote_page),
    path('update/', views.update_page),
    path('thanks/', views.thanks_page),
    path('schedule/', views.schedule_page),
    path('cart/', views.cart_page),
]
