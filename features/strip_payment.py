import requests
from django.shortcuts import render, redirect
import stripe
from django.conf import settings
from .models import TransactionModel, PropertiesSubCategory, MotorSubCategory, CompanySubCategory, ArticleSubCategory, \
    GeneralSubCategory, JobsSubCategory, Category, PlanCreation
from django.shortcuts import get_object_or_404
from users.authentication.send_mails import send_create_ad_mail
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json


stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def charge(request):
    if request.method == 'POST':
        category_id = request.session.get("category_id")
        sub_category = request.session.get("sub_category")
        form_id = request.session.get("form_id")
        plan_id = request.session.get("plan_id")
        amount = request.session.get("amount")

        # get category
        instance_category_id = get_object_or_404(Category, id=int(request.session.get("category_id", None)))

        preview_detail = None
        if category_id:
            category_id = get_object_or_404(Category, id=int(request.session.get("category_id", None)))
            sub_category_models = {
                "Properties": PropertiesSubCategory,
                "Motor": MotorSubCategory,
                "General": GeneralSubCategory,
                "Jobs": JobsSubCategory,
                "Company": CompanySubCategory,
                "Article": ArticleSubCategory,
            }
            preview_detail = sub_category_models[category_id.ad_type].objects.filter(id=int(form_id)).first()

        token = request.POST.get('stripeToken')
        amount = int(amount) if amount else 0

        plan_title = get_object_or_404(PlanCreation, id=int(plan_id))

        try:
            data = json.loads(request.body)
            intent = stripe.PaymentIntent.create(
                amount=amount*100,
                currency='usd',
                description=plan_title.plan_title,
                automatic_payment_methods={
                    'enabled': True,
                },
            )

            # create transaction
            create_transaction = TransactionModel.objects.create(
                user=request.user,
                amount=amount,
                status="InComplete",
                transaction_detail=intent,
                transaction_secret=intent['client_secret'],
                transaction_id=intent['id'],
                plan_id=get_object_or_404(PlanCreation, id=int(plan_id))
            )
            return JsonResponse({
                'clientSecret': intent['client_secret'],
                'dpmCheckerLink': f'https://dashboard.stripe.com/settings/payment_methods/review?transaction_id={intent["id"]}',
            })
            charge = stripe.Charge.create(
                amount=amount*100,
                currency='usd',
                description='Example charge',
                source=token,
            )
            create_transaction = TransactionModel.objects.create(
                user=request.user,
                amount=amount,
                status="Success",
                transaction_detail=charge,
                plan_id=get_object_or_404(PlanCreation, id=int(plan_id))
            )
            
            if preview_detail:
                preview_detail.transaction_id = create_transaction
                preview_detail.payment_status = True
                preview_detail.save()
            
            # sending email
            send_create_ad_mail(request, preview_detail.user.email)
            
            # request.session.flush()
            return redirect("post_ad_thank_you")
        except stripe.error.CardError as e:
            error_details = {
                "code": e.code if hasattr(e, 'code') else None,
                "message": e.user_message if hasattr(e, 'user_message') else str(e),
                "param": e.param if hasattr(e, 'param') else None,
                "type": "card_error"
            }
            TransactionModel.objects.create(
                user=request.user,
                amount=amount,
                status="Failed",
                transaction_detail=error_details
            )

            context = {
                "currency": preview_detail.country.currency,
                'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
                "enter_detail": preview_detail,
                "error": error_details['message']
            }
            return render(request, "users/post_ad/preview_pay.html", context)

    context = {
        "stripe_public_key": settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, "checkout.html", context)
