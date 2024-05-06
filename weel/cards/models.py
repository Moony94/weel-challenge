from decimal import Decimal
from django.db import models

class Card(models.Model):
    counter = 1111111111111111
    card_number = models.CharField(max_length=16, unique=True, null=True, blank=True)  # Remove default value
    cardholder_name = models.CharField(max_length=100)
    expiration_date = models.DateField()
    is_active = models.BooleanField(default=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Generate a card number
        if not self.card_number:
            self.card_number = str(Card.counter)
            Card.counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cardholder_name} {self.card_number}"


# Card Controls
class CardControl(models.Model):
    CONTROL_TYPES = (
        ('category', 'Category'),
        ('merchant', 'Merchant'),
        ('max_amount', 'Maximum Amount'),
        ('min_amount', 'Minimum Amount'),
    )

    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='controls')
    control_type = models.CharField(max_length=20, choices=CONTROL_TYPES)
    detail = models.CharField(max_length=100, blank=True, null=True)  # For category or merchant name
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # For amount controls

    def apply_control(self, transaction):
        if self.control_type == 'category':
            if transaction['merchant_category'] == self.detail:
                return True, ""
            else:
                return False, f"Transaction category '{transaction['merchant_category']}' does not match required category '{self.detail}'."
        elif self.control_type == 'merchant':
            if transaction['merchant'] == self.detail:
                return True, ""
            else:
                return False, f"Transaction merchant '{transaction['merchant']}' does not match required merchant '{self.detail}'."
        elif self.control_type == 'max_amount':
            if Decimal(transaction['amount']) <= self.amount:
                return True, ""
            else:
                return False, f"Transaction amount '{transaction['amount']}' exceeds the maximum allowed amount of '{self.amount}'."
        elif self.control_type == 'min_amount':
            if Decimal(transaction['amount']) >= self.amount:
                return True, ""
            else:
                return False, f"Transaction amount '{transaction['amount']}' is less than the minimum required amount of '{self.amount}'."
        return False, ""

    def __str__(self):
        return f"{self.get_control_type_display()} Control for {self.card.cardholder_name}"

