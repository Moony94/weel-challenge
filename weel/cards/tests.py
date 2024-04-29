from django.test import TestCase
from django.urls import reverse
from .models import Card, CardControl
from datetime import date
import json

class CardTests(TestCase):
    def setUp(self):
        # Creating some cards
        self.card1 = Card.objects.create(
            cardholder_name='John Doe',
            expiration_date=date(2025, 12, 31),
            balance=150.00
        )
        self.card2 = Card.objects.create(
            cardholder_name='Jane Doe',
            expiration_date=date(2024, 12, 31),
            balance=250.00
        )
        # Adding controls to card1
        self.control1 = CardControl.objects.create(
            card=self.card1,
            control_type='category',
            detail='5411'
        )
        self.control2 = CardControl.objects.create(
            card=self.card1,
            control_type='max_amount',
            amount=100.00
        )
        # Adding controls to card2
        self.control3 = CardControl.objects.create(
            card=self.card2,
            control_type='merchant',
            detail='Amazon'
        )

    def test_get_cards(self):
        response = self.client.get(reverse('cards'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['cards']), 2)

    def test_create_card(self):
        data = {
            "cardholder_name": "Alice Wonderland",
            "expiration_date": "2025-01-01",
            "balance": 300.00
        }
        response = self.client.post(reverse('cards'), json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Card.objects.count(), 3)

    def test_card_default_active_status(self):
        """Test that the card is active by default upon creation"""
        card = Card.objects.create(cardholder_name='Test User', expiration_date='2023-01-01', balance=200.00)
        self.assertTrue(card.is_active)


class CardControlTests(TestCase):
    def setUp(self):
        self.card = Card.objects.create(
            cardholder_name='Test User',
            expiration_date=date(2025, 1, 1),
            balance=200.00
        )
        self.category_control = CardControl.objects.create(
            card=self.card,
            control_type='category',
            detail='1234'
        )
        self.merchant_control = CardControl.objects.create(
            card=self.card,
            control_type='merchant',
            detail='Walmart'
        )

    def test_get_card_controls(self):
        response = self.client.get(reverse('card-controls'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['card_controls']), 2)

    def test_create_card_control(self):
        data = {
            "card_id": self.card.id,
            "control_type": "max_amount",
            "amount": 50.00
        }
        response = self.client.post(reverse('card-controls'), json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(CardControl.objects.count(), 3)

    def test_delete_card_control(self):
        control_id = self.category_control.id
        response = self.client.delete(reverse('delete-card-control', args=[control_id]))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(CardControl.objects.count(), 1)
