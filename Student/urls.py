from django.urls import path

from . import views

urlpatterns = [
    path('',views.register,name='register'),
    path('login/',views.login_page,name='login_page'),
    path('home/',views.home,name='home'),
    path('user-management/', views.user_management, name='user_management'),
    path('user-management/<int:user_id>/action/', views.manage_user, name='manage_user'),
    path('add-details/',views.add_student,name='add_student'),
    path('student-details/',views.list_students,name='list_students'),
    path('update-details/<int:pk>/',views.update_student,name='update_student'),
    path('delete-details/<int:pk>/',views.delete_student,name='delete_student'),
]