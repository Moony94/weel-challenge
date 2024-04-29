from django.db import models
from cards.models import Card

class Transaction(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    merchant = models.CharField(max_length=100)
    merchant_category = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    reason_declined = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Transaction on {self.card.card_number} for {self.amount}"

