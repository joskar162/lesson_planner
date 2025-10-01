from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.index, name='home'),
    path('lesson/<int:pk>/pdf/', views.lesson_pdf, name='lesson_pdf'),
    path('lesson/<int:pk>/docx/', views.lesson_docx, name='lesson_docx'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    # optional: keep a separate generate/ if you prefer
    # path('generate/', views.generate, name='generate'),
]