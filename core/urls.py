from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-username/', views.change_username, name='change_username'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/entries/create/', views.profile_entry_create, name='profile_entry_create'),
    path('home/entries/create/', views.home_entry_create, name='home_entry_create'),
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='core/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'), 
         name='password_reset_complete'),
    
    # URLs para colecciones
    path('collections/', views.collection_list, name='collection_list'),
    path('collections/create/', views.collection_create, name='collection_create'),
    path('collections/<int:pk>/', views.collection_detail, name='collection_detail'),
    path('collections/<int:pk>/edit/', views.collection_edit, name='collection_edit'),
    path('collections/<int:pk>/delete/', views.collection_delete, name='collection_delete'),
    
    # URLs para entradas
    path('collections/<int:collection_pk>/entries/create/', views.entry_create, name='entry_create'),
    path('entries/<int:pk>/', views.entry_detail, name='entry_detail'),
    path('entries/<int:pk>/edit/', views.entry_edit, name='entry_edit'),
    path('entries/<int:pk>/delete/', views.entry_delete, name='entry_delete'),
    path('entries/<int:pk>/toggle-favorite/', views.entry_toggle_favorite, name='entry_toggle_favorite'),
    path('entries/<int:pk>/toggle-visibility/', views.entry_toggle_visibility, name='entry_toggle_visibility'),
] 