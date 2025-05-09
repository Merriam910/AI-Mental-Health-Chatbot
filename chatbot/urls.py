from django.urls import path
from . import views
from .views import contact_view

urlpatterns = [
    path('', views.home, name='home'),  # Homepage
    path('signup/', views.signup, name='signup'),  # Signup page
    path('login/', views.login_page, name='login'),  # Login page
    path('logout/', views.logout_view, name='logout'),  # Logout page
    path('chat/', views.chat_api, name='chat'),  # Chat page (protected by login_required)
    path('chat_page/', views.chat_page, name='chat_page'),  # Optional chat page (you can remove if unnecessary)
    path('about_us/', views.about_us, name='about_us'),  # About Us page
    path('ai/', views.ai_page, name='ai_page'),  # AI page
    path('private/', views.private_page, name='private_page'),  # Private page
    path('effortless/', views.effortless_page, name='effortless_page'),  # Effortless page
    path('learnmore/', views.lm_page, name='lm_page'),  # Learn more page
    path('report/', views.contact_view, name='report_page'),  # Changed to contact_view
    path('end_conversation/', views.end_conversation, name='end_conversation'),
    path('end-session-on-close/', views.end_session_on_close, name='end_session_on_close'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),


]
