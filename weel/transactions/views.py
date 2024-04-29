from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Transaction
from cards.models import Card
import json

@csrf_exempt
@require_http_methods(["GET", "POST"])
def transactions(request):
    """
    Handle the GET and POST requests for transactions.

    If the request method is GET, return a list of all transactions in the database.
    Each transaction is represented as a dictionary with the following keys: 
    'id', 'card_id', 'amount', 'merchant', 'merchant_category', 'approved', 'reason_declined', and 'timestamp'.

    If the request method is POST, create a new transaction with the data provided in the request body.
    The request body should be a JSON object with the following keys: 
    'card', 'amount', 'merchant', and 'merchant_category'.
    The 'card' key should be the ID of the card to use for the transaction.

    The function checks if the card has sufficient balance and is active, and applies any card controls.
    If the transaction is approved, the card's balance is updated.

    Returns:
        JsonResponse: A JSON response with the list of transactions (for GET requests) or a success message 
        and the ID of the created transaction (for POST requests). If the transaction is declined or an error occurs, 
        the response will contain an error message and the reasons for the decline.
    """
    # GET path
    if request.method == 'GET':
        transactions = Transaction.objects.all()
        data = [{
            "id": transaction.id,
            "card_id": transaction.card_id,
            "amount": str(transaction.amount),
            "merchant": transaction.merchant,
            "merchant_category": transaction.merchant_category,
            "approved": transaction.approved,
            "reason_declined": transaction.reason_declined if not transaction.approved else None,
            "timestamp": transaction.timestamp.isoformat()
        } for transaction in transactions]
        return JsonResponse({"transactions": data}, safe=False)
    # POST path
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            card = Card.objects.get(id=data['card'])
            amount = Decimal(data['amount'])
            merchant = data['merchant']
            merchant_category = data['merchant_category']

            failed_controls = []

            # Check card balance and status
            if card.balance < amount or card.balance == 0:
                failed_controls.append("Insufficient funds")
            if card.is_active == False:
                failed_controls.append("Card is not active")

            # Apply card controls
            for control in card.controls.all():
                passed, failure_reason = control.apply_control(data)
                if not passed:
                    failed_controls.append(failure_reason)

            # Create transaction object regardless of control results
            transaction = Transaction.objects.create(
                card=card,
                amount=amount,
                merchant=merchant,
                merchant_category=merchant_category,
                approved=len(failed_controls) == 0,  # Transaction is approved if no failed controls
                reason_declined=", ".join(failed_controls) if failed_controls else None
            )

            # Update card balance if transaction is approved
            if transaction.approved:
                card.balance -= amount
                card.save()
                return JsonResponse({"status": "approved", "message": "Transaction approved", "transaction_id": transaction.id}, status=200)
            else:
                return JsonResponse({"status": "declined", "error": "Transaction declined", "reasons": failed_controls or ["Unknown reason"]}, status=400)

        except Card.DoesNotExist:
            return JsonResponse({"status": "declined", "error": "Card not found", "reasons": ["Card not found"]}, status=400)
        except Exception as e:
            return JsonResponse({"status": "declined", "error": str(e), "reasons": [str(e)]}, status=400)
