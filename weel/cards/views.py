from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Card, CardControl
import json

@csrf_exempt
@require_http_methods(["GET", "POST"])
def card_list(request):
    """
    Handle the GET and POST requests for the card list.

    If the request method is GET, return a list of all cards in the database.
    Each card is represented as a dictionary with the following keys: 
    'card_number', 'cardholder_name', 'expiration_date', 'is_active', and 'balance'.

    If the request method is POST, create a new card with the data provided in the request body.
    The request body should be a JSON object with the following keys: 
    'cardholder_name', 'expiration_date', 'is_active', and 'balance'.
    'is_active' defaults to True and 'balance' defaults to 0 if not specified in the request.

    Returns:
        JsonResponse: A JSON response with the list of cards (for GET requests) or a success message 
        and the ID of the created card (for POST requests). If an error occurs during a POST request, 
        the response will contain an error message.
    """
    # GET path
    if request.method == 'GET':
        cards = Card.objects.all()
        data = [{"card_number": card.card_number, "cardholder_name": card.cardholder_name, "expiration_date": card.expiration_date.strftime("%Y-%m-%d"), "is_active": card.is_active, "balance": float(card.balance)} for card in cards]
        return JsonResponse({"cards": data})

    # POST path
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)
            card = Card.objects.create(
                cardholder_name=data['cardholder_name'],
                expiration_date=data['expiration_date'],
                is_active=data.get('is_active', True),  # Defaults to True if not specified
                balance=data.get('balance', 0)  # Defaults to 0 if not specified
            )
            return JsonResponse({"message": "Card created successfully", "card_id": card.id}, status=201)
        except (TypeError, ValueError, KeyError) as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def card_controls(request):
    """
    Handle the GET and POST requests for card controls.

    If the request method is GET, return a list of all card controls in the database.
    Each control is represented as a dictionary with the following keys: 
    'id', 'card_id', 'control_type', 'detail', and 'amount'.

    If the request method is POST, create a new card control with the data provided in the request body.
    The request body should be a JSON object with the following keys: 
    'card_id', 'control_type', 'detail', and 'amount'.
    'detail' and 'amount' are optional.

    Returns:
        JsonResponse: A JSON response with the list of card controls (for GET requests) or a success message 
        and the ID of the created control (for POST requests). If an error occurs during a POST request, 
        the response will contain an error message.
    """
    # GET path
    if request.method == 'GET':
        controls = CardControl.objects.all()
        data = [
            {
                "id": control.id,
                "card_id": control.card_id,
                "control_type": control.control_type,
                "detail": control.detail,
                "amount": float(control.amount) if control.amount else None,
            } for control in controls
        ]
        return JsonResponse({"card_controls": data}, safe=False)
    
    # POST path
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            card = Card.objects.get(id=data['card_id'])
            control = CardControl.objects.create(
                card=card,
                control_type=data['control_type'],
                detail=data.get('detail'),
                amount=data.get('amount')
            )
            return JsonResponse({"message": "Card control created successfully", "control_id": control.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_card_control(request, control_id):
    """
    Handle the DELETE request for a specific card control.

    The control to delete is identified by the `control_id` parameter.

    If the control is found, it is deleted and a success message is returned.
    If the control is not found, an error message is returned.

    Returns:
        JsonResponse: A JSON response with a success message (if the control is found and deleted) 
        or an error message (if the control is not found).
    """
    try:
        control = CardControl.objects.get(id=control_id)
        control.delete()
        return JsonResponse({"message": "Card control deleted successfully"}, status=204)
    except CardControl.DoesNotExist:
        return JsonResponse({"error": "Card control not found"}, status=404)