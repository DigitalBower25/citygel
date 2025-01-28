import json
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from .models import TransactionModel
from django.shortcuts import render

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    event_type = event['type']
    event_data = event['data']['object']

    if event_type == 'checkout.session.completed':
        handle_checkout_session_completed(event_data)
    elif event_type == 'invoice.payment_succeeded':
        handle_invoice_payment_succeeded(event_data)
    elif event_type == 'invoice.payment_failed':
        handle_invoice_payment_failed(event_data)
        # Add more event handlers as needed

    return HttpResponse(status=200)


def handle_invoice_payment_succeeded(payment_intent):
    transaction_id = payment_intent.get('id')
    transaction = TransactionModel.objects.get(transaction_detail__id=transaction_id)
    transaction.status = "Success"
    transaction.save()


def handle_invoice_payment_failed(payment_intent):
    transaction_id = payment_intent.get('id')
    transaction = TransactionModel.objects.get(transaction_detail__id=transaction_id)
    transaction.status = "Failed"
    transaction.save()


def handle_checkout_session_completed(payment_intent):
    transaction_id = payment_intent.get('id')
    transaction = TransactionModel.objects.get(transaction_detail__id=transaction_id)
    transaction.status = "Success"
    transaction.save()


@csrf_exempt
def create_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            intent = stripe.PaymentIntent.create(
                amount=100,
                currency='usd',
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            return JsonResponse({
                'clientSecret': intent['client_secret'],
                'dpmCheckerLink': f'https://dashboard.stripe.com/settings/payment_methods/review?transaction_id={intent["id"]}',
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=403)
    return render(request, "checkout.html")

