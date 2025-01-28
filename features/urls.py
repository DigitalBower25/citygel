from django.urls import path
from . import views as view
from django.contrib.auth.decorators import login_required
from .strip_payment import *
from .strip_webhook import *


urlpatterns = [
    # path("emirate-category/<int:state_id>/", view.emirate_category_page, name="emirate_category_page"),
    
    path('fetch-subcategories/', view.fetch_subcategories, name='fetch_subcategories'),
    path('fetch-filtered-items/', view.fetch_filtered_items, name='fetch_filtered_items'),
    path('filter-default-data/', view.filter_default_data, name='filter_default_data'),
    
    # path("<str:country_id>/<str:state_id>/<str:category_id>/", view.emirate_home_page, name="emirate_home_page"),

    # path("category-detail/<str:ad_type>/<int:detail_id>/", view.CategoryDetailView.as_view(), name="category_detail_page"),

    path("emirate-products/", view.emirate_products_page, name="emirate_products_page"),
    # path("privacy-policy/", view.privacy_policy_page, name="privacy_policy"),
    # path("term-condition/", view.term_condition_page, name="term_condition"),
    # path("cookie-policy/", view.cookie_policy_page, name="cookie_policy"),
    # path("cancellation-policy/", view.cancellation_policy_page, name="cancellation_policy"),
    # path("contact-us/", view.contact_us_view, name="contact_us_view"),


    # post add
    path("post-ad-select-category/", login_required(view.post_ad_select_category), name="post_ad_select_category"),
    path("post-ad-select-sub-category/", login_required(view.post_ad_select_sub_category), name="post_ad_select_sub_category"),
    path("post-ad-enter-details/", login_required(view.post_ad_enter_details), name="post_ad_enter_details"),
    path("post-ad-pricing-plan/", login_required(view.post_ad_pricing_plan), name="post_ad_pricing_plan"),
    path("post-ad-preview-pay/", login_required(view.post_ad_preview_pay), name="post_ad_preview_pay"),
    path("post-ad-thank-you/", login_required(view.post_ad_thank_you), name="post_ad_thank_you"),

    # path("article-detail/<int:article_id>/", view.article_detail_page, name="article_detail_page"),

    # enquiry form
    path("add-enquiry/", login_required(view.enquiry_form_add), name="enquiry_form_add"),
    path("personal-detail-page/", login_required(view.personal_detail_page), name="personal_detail_page"),
    path("profile-update/", view.profile_update, name="profile_update"),
    path("get-states/", view.get_states, name="get_states"),
    path("get-city/", view.get_city, name="get_city"),
    path("get-sub-category/", view.get_sub_category, name="get_sub_category"),
    path("get-sub-category-type/", view.get_sub_category_type, name="get_sub_category_type"),

    # my ads delete
    path("my-ads-delete/<int:category_id>/<int:ad_id>/", login_required(view.my_ads_delete), name="my_ads_delete"),
    path("enquiry-delete/<int:enquiry_id>/", login_required(view.enquiry_delete), name="enquiry_delete"),

    # strip payment
    path("payment/", charge, name="strip_payment"),
    path('webhook/stripe/', stripe_webhook, name='stripe-webhook'),

    # path('create-payment-intent/', create_payment, name='create_payment'),


    # approved status
    path("set-approved/", login_required(view.set_approved), name="set_approved"),
    path("set-approved-motor/", login_required(view.set_approved_motor), name="set_approved_motor"),
    path("set-approved-general/", login_required(view.set_approved_general), name="set_approved_general"),
    path("set-approved-job/", login_required(view.set_approved_job), name="set_approved_job"),
    path("set-approved-company/", login_required(view.set_approved_company), name="set_approved_company"),
    path("set-approved-article/", login_required(view.set_approved_article), name="set_approved_article"),
    # path("contactUs_Page/", view.contactUsForm, name="contactUs_Page"),
]
