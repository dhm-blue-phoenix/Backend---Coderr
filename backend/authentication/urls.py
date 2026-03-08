from django.urls import path, include


urlpatterns = [
    path('', include('authentication.api.urls')),
]