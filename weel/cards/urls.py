from django.urls import path
from .views import card_list, card_controls, delete_card_control

urlpatterns = [
    path('cards/', card_list, name='cards'),
    path('card-controls/', card_controls, name='card-controls'),
    path('card-controls/<int:control_id>/', delete_card_control, name='delete-card-control'),
]
