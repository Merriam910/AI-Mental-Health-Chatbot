from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('chatbot.urls')),  # Includes the chatbot app's urls

]
from django.http import HttpResponse
urlpatterns = [
    path('health/', lambda r: HttpResponse(status=200)),
    # ... your other URLs ...
]