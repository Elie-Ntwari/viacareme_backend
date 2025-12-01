from django.urls import path
from . import views 

urlpatterns = [
    
    path('chatbot/', views.chat_view, name='chatbot_api'),

    path('predict/',views.PredictionView.as_view(), name='predict'),
]