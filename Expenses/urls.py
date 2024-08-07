from django.urls import path
from .import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('',views.home,name='home'),
    path('login',views.login_view,name='login'),
    path('register',views.register,name='register'),
    path('logout',views.logout_view,name='logout'),
    path('Admin',views.admin_view,name='Admin'),
    path('add-expenses',views.add_expense,name="add_expense"),
    path('add-trip',views.add_trip,name="add_trip"),
    path('add-category',views.add_category,name="add_category"),
    path('trips-list',views.trip_list,name="trips_list"),
    path('expense-list/<int:pk>/',views.expense_list,name="expense_list"),
    path('end-trip/<int:pk>/',views.finsih_trip,name="end_trip"),
    path('activate/<uidb64>/<token>/',views.activate_account, name='activate_account'),
    
    #password change and forget setup
    path('password-reset',auth_views.PasswordResetView.as_view(template_name='password/password_reset_form.html'),name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='password/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-done',auth_views.PasswordResetDoneView.as_view(template_name='password/password_reset_done.html'),name='password_reset_done'),
    path('password-reset-complete',auth_views.PasswordResetCompleteView.as_view(template_name='password/password_reset_complete.html'),name='password_reset_complete'),
    path('password-change',auth_views.PasswordChangeView.as_view(template_name='password/password_change.html'),name='password_change'),
    path('password-change-done',auth_views.PasswordChangeDoneView.as_view(template_name='password/password_change_complete.html'),name='password_change_done')
]