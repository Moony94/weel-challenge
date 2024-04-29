from django.test import TestCase
from django.urls import reverse
from cards.models import Card, CardControl
import json

class TransactionViewsTests(TestCase):
    def setUp(self):
        self.card = Card.objects.create(
            cardholder_name='John Doe',
            expiration_date='2023-01-01',
            balance=10000.00,
            is_active=True
        )
        # Create controls
        self.category_control = CardControl.objects.create(
            card=self.card,
            control_type='category',
            detail='food'
        )
        self.merchant_control = CardControl.objects.create(
            card=self.card,
            control_type='merchant',
            detail='Woolworths'
        )
        self.max_amount_control = CardControl.objects.create(
            card=self.card,
            control_type='max_amount',
            amount=150.00
        )
        self.min_amount_control = CardControl.objects.create(
            card=self.card,
            control_type='min_amount',
            amount=10.00
        )

    def test_transaction_approved_multiple_controls(self):
        # Assuming all controls need to pass
        data = {"card": self.card.id, "amount": "50.00", "merchant": "Woolworths", "merchant_category": "food"}
        response = self.client.post(reverse('transactions'), json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("approved", response.json()['status'])

    # Declined scenarios
    def test_transaction_declined_by_category_control(self):
        data = {"card": self.card.id, "amount": "20.00", "merchant": "Woolworths", "merchant_category": "1234"}
        response = self.client.post(reverse('transactions'), json.dumps(data), content_type="application/json")
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("declined", response.json()['status'])

    def test_transaction_declined_by_merchant_control(self):
        data = {"card": self.card.id, "amount": "20.00", "merchant": "Target", "merchant_category": "5411"}
        response = self.client.post(reverse('transactions'), json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("declined", response.json()['status'])

    def test_transaction_declined_by_max_amount_control(self):
        data = {"card": self.card.id, "amount": "200.00", "merchant": "Woolworths", "merchant_category": "5411"}
        response = self.client.post(reverse('transactions'), json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("declined", response.json()['status'])

    def test_transaction_declined_by_min_amount_control(self):
        data = {"card": self.card.id, "amount": "5.00", "merchant": "Woolworths", "merchant_category": "5411"}
        response = self.client.post(reverse('transactions'), json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("declined", response.json()['status'])

    def test_transaction_declined_insufficient_funds(self):
        self.card.balance = 1.00
        self.card.save()
        data = {"card": self.card.id, "amount": "100.00", "merchant": "Woolworths", "merchant_category": "food"}
        response = self.client.post(reverse('transactions'), json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("declined", response.json()['status'])
        self.assertIn("Insufficient funds", response.json()['reasons'])

    def test_transaction_declined_inactive_card(self):
        self.card.is_active = False
        self.card.save()
        data = {"card": self.card.id, "amount": "50.00", "merchant": "Woolworths", "merchant_category": "food"}
        response = self.client.post(reverse('transactions'), json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("declined", response.json()['status'])
        self.assertIn("Card is not active", response.json()['reasons'])

    def test_transaction_declined_multiple_failures(self):
        self.card.is_active = False
        self.card.save()
        data = {"card": self.card.id, "amount": "300.00", "merchant": "Target", "merchant_category": "1234"}
        response = self.client.post(reverse('transactions'), json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("declined", response.json()['status'])
        self.assertEqual(len(response.json()['reasons']), 4)


