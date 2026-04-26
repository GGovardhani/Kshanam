from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('life-setup/', views.life_setup_view, name='life_setup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('daily-entry/', views.daily_entry, name='daily_entry'),
    path('daily-result/', views.daily_result, name='daily_result'),
    path('weekly-report/', views.weekly_report, name='weekly_report'),
    path('monthly-report/', views.monthly_report, name='monthly_report'),
    path('health/', views.health_view, name='health'),
    path('profile/', views.profile_view, name='profile'),
    path('journal-history/', views.journal_history, name='journal_history'),
    path('insights/', views.insights_history, name='insights_history'),
]