from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from users.models import UserModel, CountryCode, TitleDescriptionState
from .models import *
from .forms import *
from .models import *
from django.contrib import messages
from .helpers import sub_category_count, sub_category_context_model, send_html_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, Max, Min
from django.views.generic import TemplateView
from django.db.models import Count
from django.views.generic import TemplateView, ListView
from django.views.decorators.http import require_GET
from django.conf import settings
from itertools import chain
import phonenumbers
from django.utils import timezone
from datetime import timedelta
import dateutil.relativedelta
from .helpers import send_html_mail
from users.authentication.send_mails import send_ad_approve_mail, send_ad_reject_mail

from django.template.loader import render_to_string
from django.db.models import F
from users.authentication.send_mails import send_create_ad_mail
import json
import stripe


def emirate_category_page(request, country_code, state_id):
    country = get_object_or_404(CountryCode, slug=country_code)
    # get_state_id = request.GET.get("state_id")
    # if get_state_id:
    #     state_id = int(get_state_id)

    state_id = get_object_or_404(State, slug=state_id, country=country)
    state_id = state_id.id

    state_instance = get_object_or_404(State, id=int(state_id))
    category_filter = Category.objects.filter(state=state_instance)
    request.session['header_state_id'] = state_id

    if state_id:
        mobile_footer = FooterBanners.objects.filter(type="mobile", state=state_id).first()
        desktop_footer = FooterBanners.objects.filter(type="desktop", state=state_id).first()
    else:
        mobile_footer = FooterBanners.objects.filter(type="mobile").first()
        desktop_footer = FooterBanners.objects.filter(type="desktop").first()
    context = {
        "category_filter": category_filter,
        "state_id": state_id,
        "mobile_footer_images": mobile_footer,
        "desktop_footer_images": desktop_footer,
        "state_instance": state_instance,
        "title_des": TitleDescriptionState.objects.filter(state=state_instance).first()
    }
    return render(request, "users/features/emirate_services.html", context)


def fetch_subcategories(request):
    session_state_id = request.session.get("header_state_id")
    category_id = request.GET.get('category_id')
    cat = get_object_or_404(Category, slug=category_id, state=session_state_id)
    
    if cat:
        subcategories = SubCategoryModel.objects.filter(category_id=cat)
        subcategory_html = render_to_string('users/features/filter/sub_category.html', {'sub_category_fil': subcategories,})

        sub_category_models = {
            "Properties": PropertiesSubCategory,
            "Motor": MotorSubCategory,
            "General": GeneralSubCategory,
            "Jobs": JobsSubCategory,
            "Company": CompanySubCategory,
            "Article": ArticleSubCategory,
        }
        if session_state_id:
            item_list = (
                sub_category_models.get(cat.ad_type, None).objects.filter(state=session_state_id)
                if cat.ad_type in sub_category_models
                else None
            )
            
        item_list = item_list.filter(approved = True)
    
        # Exclude items with end_date less than today
        today = timezone.now().date()
        item_list = item_list.filter(end_date__gte=today)
        min_price = item_list.aggregate(Min('total_price'))['total_price__min']
        max_price = item_list.aggregate(Max('total_price'))['total_price__max']
        if not min_price:
            min_price = 0
        if not max_price:
            max_price = 0
        
        paginator = Paginator(item_list, 9)
        page = request.GET.get("page")

        try:
            items = paginator.page(page) if paginator else []
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        sub_cat_list = SubCategoryModel.objects.filter(category=cat).values_list('id', flat=True).distinct()
        motor = MotorSubCategory.objects.filter(approved=True,  end_date__gte=today, state=session_state_id)
            
        context = {
        "item_list": items,
        "category_instance": cat,
        "city_states":City.objects.filter(state=session_state_id),
        "min_price":min_price,
        "max_price":max_price,
        "category_instance": cat,
        "all_category":Category.objects.filter(state=session_state_id),
        "sub_category_fil": SubCategoryModel.objects.filter(category=cat),
        "ad_banners": AdBanner.objects.select_related().filter(category=cat, ad_side="top", page_type="listing_page"),
        "first_ad_banners": AdBanner.objects.filter(category=cat, ad_side="top", page_type="listing_page").first(),
        "first_bottom_ad_banners": AdBanner.objects.filter(category=cat, ad_side="bottom", page_type="listing_page").first(),
        
        }
        filter_html = render_to_string('users/features/filter/filter_category_fields.html', context)
        html = render_to_string('users/features/filter/filter_data_display.html', context)
        filter_sort_by_html = render_to_string('users/features/filter/sort_by.html', context)
        first_ad_banners = AdBanner.objects.select_related().filter(category=cat, ad_side="top", page_type="listing_page").first(),
        banner_html = render_to_string('users/features/filter/top_banner.html', {"first_ad_banners":first_ad_banners}) 
        first_bottom_ad_banners = AdBanner.objects.select_related().filter(category=cat, ad_side="bottom", page_type="listing_page").first(),
        side_banner_html = render_to_string('users/features/filter/side_banner.html', {"first_bottom_ad_banners":first_bottom_ad_banners}) 
        response_data = {
            'subcategories': subcategory_html,
            'ad_type': cat.ad_type,
            'html': html,
            'bannerhtml':banner_html,
            'sidebannerhtml':side_banner_html,
            'filterhtml':filter_html,
            'filtersortbyhtml':filter_sort_by_html,
          
        }
    return JsonResponse(response_data)


def fetch_filtered_items(request):
    category_id = request.GET.get("category_id", "")
    state_id =  request.session.get("header_state_id")
    category_instance = get_object_or_404(Category, slug=category_id)
    sub_category_id = request.GET.get("sub_category_id", "")
    
    sub_category_models = {
        "Properties": PropertiesSubCategory,
        "Motor": MotorSubCategory,
        "General": GeneralSubCategory,
        "Jobs": JobsSubCategory,
        "Company": CompanySubCategory,
        "Article": ArticleSubCategory,
    }
    if sub_category_id:
        sub_category_instance = get_object_or_404(SubCategoryModel, id=sub_category_id)
        item_list = (
            sub_category_models.get(category_instance.ad_type, None).objects.filter(
                sub_category=sub_category_instance, state=state_id
            )
            if category_instance.ad_type in sub_category_models
            else None
        )
        rooms =  RoomsModel.objects.filter(sub_category=sub_category_instance).order_by('name').distinct('name')
       
    else:
        item_list = (
            sub_category_models.get(category_instance.ad_type, None).objects.filter(state=state_id)
            if category_instance.ad_type in sub_category_models
            else None
        )
        rooms = RoomsModel.objects.none() 
    item_list = item_list.filter(approved = True)
    
    today = timezone.now().date()
    item_list = item_list.filter(end_date__gte=today)
    
    min_price = item_list.aggregate(Min('total_price'))['total_price__min']
    max_price = item_list.aggregate(Max('total_price'))['total_price__max']
    if not min_price:
        min_price = 0
    if not max_price:
            max_price = 0
    
    sort_by = request.GET.get("sort_by", "")
    if sort_by:
        sort_options = sort_by.split(',')
        if category_instance.ad_type == 'Article':
            if 'sort_by_date' in sort_options:
                item_list = item_list.order_by('-created_at') 
            if 'sort_by_low_price' in sort_options:
                item_list = item_list.order_by('created_at')
            if 'sort_by_high_price' in sort_options:
                item_list = item_list.order_by('-created_at')
        else:
            if 'sort_by_date' in sort_options:
                item_list = item_list.order_by('-created_at') 
            if 'sort_by_low_price' in sort_options:
                item_list = item_list.order_by('total_price')
            if 'sort_by_high_price' in sort_options:
                item_list = item_list.order_by('-total_price')
    sub_cat_list = SubCategoryModel.objects.filter(category=category_instance).values_list('id', flat=True).distinct()
    if sub_category_id:
        sub_cat_list = [sub_category_id]

    paginator = Paginator(item_list, 9)
    page = request.GET.get("page")

    try:
        items = paginator.page(page) if paginator else []
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    
    motor = MotorSubCategory.objects.filter(approved=True,  end_date__gte=today, state=state_id)   
    context = {
        "item_list": items,
        "min_price":min_price,
        "max_price":max_price,
        "category_instance": category_instance,
        'ad_type': category_instance.ad_type ,
        "rooms": rooms,
        "type":SubCategoryType.objects.filter(sub_category__in=list(sub_cat_list)).order_by('type_name'),
       
        }
    context1 = {
        "city_states":City.objects.filter(state=state_id),
        "type":SubCategoryType.objects.filter(sub_category__in=list(sub_cat_list)).order_by('type_name').distinct('type_name'),
        "category_instance":category_instance,
        'rooms':  RoomsModel.objects.filter(sub_category=sub_category_id).order_by('name').distinct('name'),
        'listed_by':  ListedByModel.objects.filter(sub_category=sub_category_id).order_by('name').distinct('name'),
        'motor_brand':  MotorBrand.objects.all().order_by('name').distinct('name'),
        'motor_year' : motor.order_by('year').distinct('year'),
        'motor_owners' : motor.order_by('no_of_owners').distinct('no_of_owners'),
        'motor_trans' : motor.values('transmission__name').distinct().order_by('transmission__name'),
        'no_of_owner':  MotorSubCategory.objects.filter(approved=True, end_date__gte=today, state=state_id).order_by('no_of_owners').distinct('no_of_owners'),
        'transmission':  TransmissionModel.objects.filter(sub_category=sub_category_id).order_by('name').distinct('name'),
    }
    filter_html = render_to_string('users/features/filter/filter_category_fields.html', context1)
    html = render_to_string('users/features/filter/filter_data_display.html', context)

    return JsonResponse({'html': html, 'filterhtml':filter_html})


def filter_default_data(request):
    category_id = request.GET.get("category_id", "")
    state_id =  request.session.get("header_state_id")
    city = request.GET.get("city", "")
    sub_type = request.GET.get("sub_type", "")
    rooms = request.GET.get("rooms", "")
    listed_by = request.GET.get("listed_by", "")
    brand = request.GET.get("brand", "")
    year = request.GET.get("year", "")
    no_of_owner = request.GET.get("no_of_owner", "")
    transmission = request.GET.get("transmission", "")
    category_instance = get_object_or_404(Category, slug=category_id)
    sub_category_id = request.GET.get("sub_category_id", "")
    
     # Price range
    min_price = request.GET.get("min_price", None)
    max_price = request.GET.get("max_price", None)
    
    sub_category_models = {
        "Properties": PropertiesSubCategory,
        "Motor": MotorSubCategory,
        "General": GeneralSubCategory,
        "Jobs": JobsSubCategory,
        "Company": CompanySubCategory,
        "Article": ArticleSubCategory,
    }
    if sub_category_id:
        sub_category_instance = get_object_or_404(SubCategoryModel, id=sub_category_id)
        item_list = (
            sub_category_models.get(category_instance.ad_type, None).objects.filter(
                sub_category=sub_category_instance, state=state_id
            )
            if category_instance.ad_type in sub_category_models
            else None
        )
    else:
        item_list = (
            sub_category_models.get(category_instance.ad_type, None).objects.filter(state=state_id)
            if category_instance.ad_type in sub_category_models
            else None
        )
    item_list = item_list.filter(approved = True)
    
    today = timezone.now().date()
    item_list = item_list.filter(end_date__gte=today)
    
    if city:
        item_list = item_list.filter(city=city)
    else:
        item_list = item_list.filter(end_date__gte=today)
    if sub_type:
        item_list = item_list.filter(type=sub_type)
    else:
        item_list = item_list.filter(end_date__gte=today)
    if rooms:
        item_list = item_list.filter(rooms=rooms)
    else:
        item_list = item_list.filter(end_date__gte=today)
    if listed_by:
        item_list = item_list.filter(listed_by=listed_by)
    else:
        item_list = item_list.filter(end_date__gte=today)
    if brand:
        item_list = item_list.filter(brand=brand)
    else:
        item_list = item_list.filter(end_date__gte=today)
    if year:
        item_list = item_list.filter(year=year)
    else:
        item_list = item_list.filter(end_date__gte=today)
    if no_of_owner:
        item_list = item_list.filter(no_of_owners=no_of_owner)
    else:
        item_list = item_list.filter(end_date__gte=today)
    if transmission:
        item_list = item_list.filter(transmission=transmission)
    else:
        item_list = item_list.filter(end_date__gte=today)
    if city and sub_type:
        item_list = item_list.filter(type=sub_type, city=city)
    else:
        item_list = item_list.filter(end_date__gte=today)
   
    if min_price or max_price:
        item_list = item_list.filter(total_price__gte=min_price, total_price__lte=max_price)

    sort_by = request.GET.get("sort_by", "")
    if sort_by:
        sort_options = sort_by.split(',')
        if 'sort_by_date' in sort_options:
            item_list = item_list.order_by('-created_at') 
        if 'sort_by_low_price' in sort_options:
            item_list = item_list.order_by('total_price')
        if 'sort_by_high_price' in sort_options:
            item_list = item_list.order_by('-total_price')
        
    paginator = Paginator(item_list, 9)
    page = request.GET.get("page")

    try:
        items = paginator.page(page) if paginator else []
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    
    context = {
        "item_list":items,
        "category_instance": category_instance,
    }
    html = render_to_string('users/features/filter/filter_data_display.html', context)

    return JsonResponse({'html': html})


def emirate_home_page(request, country_id, state_id, category_id):
    category_instance = get_object_or_404(Category, slug=category_id)
    state_id = get_object_or_404(State, slug=state_id)
    request.session["header_state_id"] = state_id.id
   
    sub_category_models = {
        "Properties": PropertiesSubCategory,
        "Motor": MotorSubCategory,
        "General": GeneralSubCategory,
        "Jobs": JobsSubCategory,
        "Company": CompanySubCategory,
        "Article": ArticleSubCategory,
    }
    # if session_state_id:
    item_list = (
        sub_category_models.get(category_instance.ad_type, None).objects.filter(state=state_id)
        if category_instance.ad_type in sub_category_models
        else None
    )
        
    item_list = item_list.filter(approved = True)
    
    # Exclude items with end_date less than today
    today = timezone.now().date()
    item_list = item_list.filter(end_date__gte=today)
    min_price = item_list.aggregate(Min('total_price'))['total_price__min']
    max_price = item_list.aggregate(Max('total_price'))['total_price__max']
    if not min_price:
        min_price = 0
    if not max_price:
        max_price = 0
    
    paginator = Paginator(item_list, 9)
    page = request.GET.get("page")

    try:
        items = paginator.page(page) if paginator else []
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    # sub_cat_list = SubCategoryModel.objects.filter(category=category_instance).values_list('id', flat=True).distinct()
    # motor = MotorSubCategory.objects.filter(approved=True,  end_date__gte=today, state=session_state_id)
    context = {
        "state_id":state_id,
        "item_list":items,
        "min_price":min_price,
        "max_price":max_price,
        "city_states":City.objects.filter(state=state_id),
        "category_instance": category_instance,
        "all_category":Category.objects.filter(state=state_id),
        "sub_category_fil": SubCategoryModel.objects.filter(category=category_instance),
        "ad_banners": AdBanner.objects.select_related().filter(category=category_instance, ad_side="top", page_type="listing_page"),
        "first_ad_banners": AdBanner.objects.filter(category=category_instance, ad_side="top", page_type="listing_page").first(),
        "first_bottom_ad_banners": AdBanner.objects.filter(category=category_instance, types="desktop", ad_side="bottom", page_type="listing_page").first(),
        "first_bottom_ad_banners_mobile": AdBanner.objects.filter(category=category_instance, types="mobile", ad_side="bottom", page_type="listing_page").first(),

    }
    
    return render(request, "users/features/emirate_home.html", context)



class CategoryDetailView(TemplateView):
    template_name = "users/features/category_detail.html"

    # Mapping of ad types to models and image fields
    ad_type_mapping = {
        "Properties": (PropertiesSubCategory, "properties_sub_category"),
        "Motor": (MotorSubCategory, "motor_sub_category"),
        "General": (GeneralSubCategory, "general_sub_category"),
        "Jobs": (JobsSubCategory, None),
        "Company": (CompanySubCategory, None),
        "Article": (ArticleSubCategory, "articles_sub_category"),
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        detail_id = kwargs.get("detail_name")
        ad_type = kwargs.get("ad_type")
        state_slug = kwargs.get("state_id")
        ad_type = get_object_or_404(Category, slug=ad_type).ad_type

        if ad_type in self.ad_type_mapping:
            model, image_field = self.ad_type_mapping[ad_type]
            sub_category_list = get_object_or_404(model, slug=detail_id)
          
            images = None
            if image_field:
                images = SubCategoryImages.objects.select_related().filter(
                    **{image_field: sub_category_list}
                )

            if self.request.user.is_authenticated:
                enquiry_form =EnquiryForm(ad_type=ad_type, initial={'name': self.request.user.full_name, 'email': self.request.user.email})
            else:
                enquiry_form = None
            # Populate the context with required data
            today = timezone.now().date()
            product = model.objects.filter(end_date__gte=today, approved=True).exclude(id=sub_category_list.id)
            currency = ''
            session_state_id = get_object_or_404(State, slug=state_slug)
            if session_state_id:
                country_filter = State.objects.filter(slug=session_state_id.id).values("country")
                country = CountryCode.objects.filter(id__in=country_filter).order_by('currency').distinct('currency')
                for obj in country:
                    currency = obj.currency
                product = model.objects.filter(end_date__gte=today, approved=True, state=session_state_id).exclude(id=sub_category_list.id)
            context.update(
                {
                    "currency":currency,
                    "sub_category_list": sub_category_list,
                    "images": images,
                    "products": product,
                    "forms": {
                        "form": enquiry_form,
                        "sub_category": (
                            sub_category_list.sub_category.id
                            if getattr(sub_category_list, "sub_category", None)
                            else None
                        ),
                        "ad_title": sub_category_list.ad_title,
                        "ad_user": sub_category_list.user.id,
                    },
                    "contact_us": {
                        "name": sub_category_list.user.full_name,
                        "mobile_number": sub_category_list.user.mobile_number,
                        "email": sub_category_list.user.email,
                        "price": sub_category_list.total_price,
                        "country": sub_category_list.country,
                        "state": sub_category_list.state,
                    },
                    "first_bottom_ad_banners": AdBanner.objects.filter(sub_category=sub_category_list.sub_category.id, page_type="detail_page").first(),
                    "all_bottom_ad_banners": AdBanner.objects.filter(sub_category=sub_category_list.sub_category.id, page_type="detail_page"),
                    "enquiry_type": sub_category_list.enquiry_type,
                }
            )
        return context


def article_detail_page(request, country_slug, state_slug, article_id):
    instance = get_object_or_404(ArticleSubCategory, slug=article_id)
    ad_banner = AdBanner.objects.filter(sub_category=instance.sub_category, page_type="article_page")
    context = {
        "article_details": instance,
        "ad_banner": ad_banner.first()
    }
    return render(request, "users/features/article_page.html", context)


def post_ad_select_category(request):
    category_id = request.GET.get("category_id", None)
    if category_id:
        request.session["category_id"] = category_id
        return redirect("post_ad_select_sub_category")
    all_category = Category.objects.all()
    return render(
        request, "users/post_ad/select_category.html", {"all_category": all_category}
    )


def post_ad_select_sub_category(request):
    sub_category = request.GET.get("sub_category")
    category_id = request.session.get("category_id", None)
    category = get_object_or_404(Category, id=int(category_id))
    sub_category_choices = None
    try:
        sub_category_choices = get_list_or_404(SubCategoryModel, category=int(category_id))
    except Exception as e:
        sub_category_choices = None

    if sub_category:
        request.session["sub_category"] = sub_category
        return redirect("post_ad_enter_details")
    context = {
        "category_item": category,
        "sub_category_choices": sub_category_choices,
    }
    return render(request, "users/post_ad/select_sub_category.html", context)


def post_ad_enter_details(request):
    category_id = request.session.get("category_id", None)
    sub_category = request.session.get("sub_category", None)

    category_instance = get_object_or_404(Category, id=int(category_id))

    if category_instance.ad_type == "Properties":
        form = PropertiesAdForm(request.POST or None, sub_category=sub_category or None)
        image_save_model = "properties_sub_category"
    elif category_instance.ad_type == "Motor":
        form = MotorAdForm(request.POST or None, sub_category=sub_category or None)
        image_save_model = "motor_sub_category"
    elif category_instance.ad_type == "Jobs":
        form = JobsAdForm(request.POST or None, sub_category=sub_category or None)
        image_save_model = None
    elif category_instance.ad_type == "Company":
        form = CompanyAdForm(request.POST or None, sub_category=sub_category or None)
        image_save_model = None
    elif category_instance.ad_type == "Article":
        form = ArticleAdForm(request.POST or None, sub_category=sub_category or None)
        image_save_model = "articles_sub_category"
    else:
        form = GeneralAdForm(request.POST or None, sub_category=sub_category or None)
        image_save_model = "general_sub_category"
        
    sub = get_object_or_404(SubCategoryModel, id=int(sub_category))
    
    if request.method == "POST":
        form.instance.sub_category = get_object_or_404(
            SubCategoryModel, id=int(sub_category)
        )
        form.instance.category = get_object_or_404(Category, id=int(category_id))
        form.instance.user = request.user
        if form.is_valid():
            form_instance = form.save()
            request.session["form_id"] = form_instance.id

            if image_save_model:
                main_image = request.FILES.getlist("main_image")
                for image in main_image:
                    SubCategoryImages.objects.create(
                        **{image_save_model: form_instance, "images": image}
                    )

            return redirect("post_ad_pricing_plan")
        else:
            return render(request, "users/post_ad/enter_details.html",
                          {"form": form, "image_save_model": image_save_model})
    else:
        context = {
            "form": form,
            "image_save_model": image_save_model,
            "first_ad_banners": AdBanner.objects.filter(sub_category=sub, page_type="ad_creation_page").first(),
            "all_bottom_ad_banners": AdBanner.objects.filter(sub_category=sub, page_type="ad_creation_page")
        }
        return render(request, "users/post_ad/enter_details.html", context)


def post_ad_pricing_plan(request):
    category_get = get_object_or_404(Category, id=int(request.session.get("category_id", None)))
    all_plan = PlanCreation.objects.select_related().filter(category=category_get).order_by("price")
    plan_id = request.GET.get("plan_id", None)
    amount = request.GET.get("amount", None)
    if plan_id:
        request.session['plan_id'] = plan_id
        request.session['amount'] = amount
        return redirect("post_ad_preview_pay")
    return render(request, "users/post_ad/pricing_plan.html", {"all_plan": all_plan})


def post_ad_preview_pay(request):
    form_id = request.session.get("form_id")
    category_id = get_object_or_404(Category, id=int(request.session.get("category_id", None)))
    session_state_id = request.session.get("header_state_id")
    currency = ''

    if session_state_id:
        country_filter = State.objects.filter(id=int(session_state_id)).values("country")
        state = State.objects.filter(country__in=country_filter)
        print("country_filter",country_filter)
        country = CountryCode.objects.filter(id__in=country_filter).order_by('currency').distinct('currency')
        for obj in country:
            currency = obj.currency
    if category_id:
        sub_category_models = {
            "Properties": PropertiesSubCategory,
            "Motor": MotorSubCategory,
            "General": GeneralSubCategory,
            "Jobs": JobsSubCategory,
            "Company": CompanySubCategory,
            "Article": ArticleSubCategory,
        }
        preview_detail = sub_category_models[category_id.ad_type].objects.get(id=int(form_id))

        # when plan free
        get_amount = request.session.get("amount")
        if get_amount in ['0', 0, 0.0]:
            plan_id = request.session.get("plan_id")
            create_transaction = TransactionModel.objects.create(
                user=request.user,
                amount=get_amount,
                status="Success",
                transaction_detail="",
                plan_id=get_object_or_404(PlanCreation, id=int(plan_id))
            )

            preview_detail.transaction_id = create_transaction
            preview_detail.payment_status = True
            preview_detail.save()

            # sending email
            send_create_ad_mail(request, preview_detail.user.email)

            return redirect("post_ad_thank_you")

    context = {
        "currency":currency,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        "enter_detail": preview_detail
    }
    return render(request, "users/post_ad/preview_pay.html", context)


def post_ad_thank_you(request):
    form_id = request.session.get("form_id")
    category_id = get_object_or_404(Category, id=int(request.session.get("category_id", None)))
    session_state_id = request.session.get("header_state_id")
    currency = ''
    if session_state_id:
        country_filter = State.objects.filter(id=int(session_state_id)).values("country")
        state = State.objects.filter(country__in=country_filter)
        country = CountryCode.objects.filter(id__in=country_filter).order_by('currency').distinct('currency')
        for obj in country:
            currency = obj.currency
    sub_category_models = {
        "Properties": PropertiesSubCategory,
        "Motor": MotorSubCategory,
        "General": GeneralSubCategory,
        "Jobs": JobsSubCategory,
        "Company": CompanySubCategory,
        "Article": ArticleSubCategory,
    }
    preview_detail = sub_category_models[category_id.ad_type].objects.get(id=int(form_id))

    payment_id = request.GET.get("payment_intent")
    payment_secret = request.GET.get("payment_intent_client_secret")
    status = request.GET.get("redirect_status")
    if payment_id and payment_secret and status == "succeeded":
        check_transaction = TransactionModel.objects.select_related('user').filter(
            transaction_id=payment_id, status="InComplete", transaction_secret=payment_secret, user=request.user).first()
        if check_transaction:
            #update strip json
            payment_intent = stripe.PaymentIntent.retrieve(payment_id)
            charge_id = payment_intent['latest_charge']
            charge = stripe.Charge.retrieve(charge_id)

            check_transaction.transaction_detail = charge
            check_transaction.status = "Success"
            check_transaction.save()
            preview_detail.transaction_id = check_transaction
            preview_detail.payment_status = True
            preview_detail.save()

            send_create_ad_mail(request, preview_detail.user.email)
    context = {
        "currency":currency,
        "enter_detail": preview_detail
    }
    return render(request, "users/post_ad/thank_you.html", context)


def emirate_products_page(request):
    return render(request, "users/features/emirate_products.html")


def personal_detail_page(request):
    my_enquiries = EnquiryModel.objects.filter(ad_user=request.user)

    # Helper function to fetch ads with ad_type
    def fetch_ads(model, ad_type):
        return list(
            model.objects.select_related('category').filter(user=request.user).values(
                'id', 'created_at', 'ad_title', 'approved', 'description', 'total_price', 'category', 'transaction',
                'end_date', 'start_date', 'country', 'state', 'slug', 'expired'
            ).annotate(ad_type=F('category__slug'))
        )

    properties = fetch_ads(PropertiesSubCategory, 'Properties')
    motors = fetch_ads(MotorSubCategory, 'Motor')
    generals = fetch_ads(GeneralSubCategory, 'General')
    jobs = fetch_ads(JobsSubCategory, 'Jobs')
    companies = fetch_ads(CompanySubCategory, 'Company')
    articles = fetch_ads(ArticleSubCategory, 'Article')

    combined = sorted(
        chain(properties, motors, generals, jobs, companies, articles),
        key=lambda x: x['created_at'],
        reverse=True
    )

    transaction_ids = [item['transaction'] for item in combined if item['transaction']]
    transactions_with_plans = TransactionModel.objects.select_related('plan_id').filter(id__in=transaction_ids)
    plan_titles = {transaction.id: transaction.plan_id.plan_title for transaction in transactions_with_plans}

    # Add plan titles to the combined ads
    for ad in combined:
        ad['country_code'] = get_object_or_404(CountryCode, id=int(ad['country'])).slug
        ad['state_id'] = get_object_or_404(State, id=int(ad['state'])).slug
        if ad['transaction']:
            ad['tran_amount'] = get_object_or_404(TransactionModel, id=int(ad['transaction'])).amount

        if ad['transaction'] in plan_titles:
            ad['plan_title'] = plan_titles[ad['transaction']]
        else:
            ad['plan_title'] = 'Unknown'  # Fallback if no plan title is found

        ad['start_date_formatted'] = ad.get('start_date', '').strftime('%b %d, %Y') if ad.get(
            'start_date') else 'N/A'
        ad['end_date_formatted'] = ad.get('end_date', '').strftime('%b %d, %Y') if ad.get('end_date') else 'N/A'

    paginator = Paginator(my_enquiries, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    ads_paginator = Paginator(combined, 10)
    ads_page_number = request.GET.get('ads_page')
    try:
        ads_page_obj = ads_paginator.get_page(ads_page_number)
    except PageNotAnInteger:
        ads_page_obj = ads_paginator.get_page(1)
    except EmptyPage:
        ads_page_obj = ads_paginator.get_page(ads_paginator.num_pages)
    todayss = timezone.now().date()

    context = {
        "user_detail": get_object_or_404(UserModel, id=request.user.id),
        "item_list": page_obj,
        "ads_page_obj": ads_page_obj,
        "todayss": todayss,
        "form": ProfileUpdateForm(request.POST or None, instance=request.user or None),
        "plan_titles": plan_titles
    }
    return render(request, "users/features/personal_detail_page.html", context)


def privacy_policy_page(request):
    return render(request, "users/features/privacy_policy.html")


def term_condition_page(request):
    return render(request, "users/features/term_condition.html")


def cookie_policy_page(request):
    return render(request, "users/features/cookie_policy.html")


def cancellation_policy_page(request):
    return render(request, "users/features/cancellation_policy.html")


def enquiry_form_add(request):
    if request.method == "POST":
        # get slug value
        country_slug = request.POST.get("country_slug")
        state_slug = request.POST.get("state_slug")
        category_slug = request.POST.get("category_slug")
        ad_slug = request.POST.get("ad_slug")

        ad_type = request.POST.get("ad_type")
        detail_id = request.POST.get("detail_id")
        cv_file = request.FILES.get("cv")
        form = EnquiryForm(request.POST, request.FILES or None)
        form.instance.sub_category = get_object_or_404(
            SubCategoryModel, id=request.POST.get("sub_category")
        )
        form.instance.ad_user = get_object_or_404(UserModel, id=int(request.POST.get("ad_user")))
        form.instance.ad_title = request.POST.get("ad_title")
        form.instance.phone_number = f"+{request.user.country_code.country_phone_code}{request.user.mobile_number}"
        if cv_file:
            form.instance.cv = cv_file
        if form.is_valid():
            form.save()
            messages.success(request, "Your Enquiry submitted")
            
            return redirect("category_detail_page", country_code=country_slug, state_id=state_slug,
                            ad_type=category_slug, detail_name=ad_slug)


def profile_update(request):
    if request.method != "POST":
        return redirect("personal_detail_page")

    form = ProfileUpdateForm(request.POST,request.FILES, instance=request.user)
    country_code = request.POST.get("country_code")
    phone_number = request.POST.get("mobile_number")

    try:
        # Fetch country phone code and construct full number
        instance_country = get_object_or_404(CountryCode, id=int(country_code))
        full_number = f"+{instance_country.country_phone_code}{phone_number}"

        # Validate phone number
        parsed_number = phonenumbers.parse(full_number, None)
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValueError("Phone number is not valid for the specified country.")

        if form.is_valid():
            form.save()
            messages.info(request, "Profile updated.")
        else:
            messages.warning(request, f"Profile not updated, error: {form.errors}")

    except (ValueError, CountryCode.DoesNotExist) as e:
        messages.warning(request, str(e))

    except phonenumbers.phonenumberutil.NumberParseException:
        messages.warning(request, "Invalid phone number format.")

    return redirect("personal_detail_page")


# @require_GET
# def get_states(request):
#     country_id = request.GET.get('country_id')
#     if country_id:
#         states = State.objects.filter(country=country_id).values('id', 'state', 'city')
#         state_list = list(states)
#         return JsonResponse(state_list, safe=False)
#     return JsonResponse([], safe=False)

@require_GET
def get_states(request):
    country_id = request.GET.get('country_id')
    if country_id:
        states = State.objects.filter(country=country_id).values('id', 'state')
        state_list = list(states)
        seen_states = set()
        unique_states = []
        for state in state_list:
            if state['state'] not in seen_states:
                unique_states.append(state)
                seen_states.add(state['state'])
        return JsonResponse(unique_states, safe=False)
    return JsonResponse([], safe=False)


@require_GET
def get_city(request):
    state_id = request.GET.get('state_id')
    if state_id:
        city = City.objects.filter(state=state_id).values('id', 'city')
        city_list = list(city)
        return JsonResponse(city_list, safe=False)
    return JsonResponse([], safe=False)

@require_GET
def get_sub_category(request):
    category_id = request.GET.get('category_id')
    if category_id:
        sub_categorys = SubCategoryModel.objects.filter(category=category_id).values('id', 'category', 'sub_category')
        sub_category_list = list(sub_categorys)
        return JsonResponse(sub_category_list, safe=False)
    return JsonResponse([], safe=False)


@require_GET
def get_sub_category_type(request):
    sub_category_id = request.GET.get('sub_category_id')
    if sub_category_id:
        sub_category_types = SubCategoryType.objects.filter(sub_category=sub_category_id).values('id', 'type_name')
        sub_category_list_type = list(sub_category_types)
        return JsonResponse(sub_category_list_type, safe=False)
    return JsonResponse([], safe=False)


def my_ads_delete(request, category_id, ad_id):
    category_instance = get_object_or_404(Category, id=int(category_id))
    get_model = sub_category_context_model(category_instance.ad_type)
    if get_model:
        instance = get_object_or_404(get_model, id=ad_id).delete()
    messages.success(request, "ads deleted..!")
    # return redirect("personal_detail_page")
    return redirect(request.META.get('HTTP_REFERER', 'my_ads_list'))


def enquiry_delete(request, enquiry_id):
    category_instance = get_object_or_404(EnquiryModel, id=int(enquiry_id)).delete()
    messages.success(request, "Enquiry deleted..!")
    return redirect(request.META.get('HTTP_REFERER', 'personal_detail_page'))


def set_approved(request):
    approved_ids = request.GET.getlist('approved_ids[]')
    option_type = request.GET.get('option_type')
    if approved_ids:
        prop_instances = PropertiesSubCategory.objects.filter(id__in=approved_ids)
        
        for prop_instance in prop_instances:
            # Set approved to True
            approved_status = True
            if option_type == 'rejected':
                approved_status = False
                prop_instance.expired = True
            prop_instance.approved = approved_status

            # Set start date to now
            start_date = timezone.now().date()

            # Get associated plan details
            transaction = prop_instance.transaction
            if transaction and transaction.plan_id and not prop_instance.expired:
                plan = transaction.plan_id
                if plan.validity_type == "Days":
                    end_date = start_date + timedelta(days=plan.validity)
                elif plan.validity_type == "Weeks":
                    end_date = start_date + timedelta(weeks=plan.validity)
                elif plan.validity_type == "Month":
                    end_date = start_date + dateutil.relativedelta.relativedelta(months=plan.validity)
                elif plan.validity_type == "Year":
                    end_date = start_date + dateutil.relativedelta.relativedelta(years=plan.validity)
                else:
                    end_date = None 

                # Set start_date and end_date
                prop_instance.start_date = start_date
                prop_instance.end_date = end_date
            elif prop_instance.expired:
                prop_instance.end_date = None
            prop_instance.save()

            msg = "Successfully updated."
            if option_type == 'rejected':
                send_ad_reject_mail(request, prop_instance.user.email)
            else:
                send_ad_approve_mail(request, prop_instance.user.email, prop_instance)
            
    else:
        msg = "Approved set to False for all."

    return JsonResponse({"msg": msg}, safe=False)



def set_approved_motor(request):
    approved_ids = request.GET.getlist('approved_ids[]')
    option_type = request.GET.get('option_type')
    if approved_ids:
        prop_instances = MotorSubCategory.objects.filter(id__in=approved_ids)
        
        for prop_instance in prop_instances:
            # Set approved to True
            approved_status = True
            if option_type == 'rejected':
                approved_status = False
                prop_instance.expired = True
            prop_instance.approved = approved_status

            # Set start date to now
            start_date = timezone.now().date()

            # Get associated plan details
            transaction = prop_instance.transaction
            if transaction and transaction.plan_id and not prop_instance.expired:
                plan = transaction.plan_id
                if plan.validity_type == "Days":
                    end_date = start_date + timedelta(days=plan.validity)
                elif plan.validity_type == "Weeks":
                    end_date = start_date + timedelta(weeks=plan.validity)
                elif plan.validity_type == "Month":
                    end_date = start_date + dateutil.relativedelta.relativedelta(months=plan.validity)
                elif plan.validity_type == "Year":
                    end_date = start_date + dateutil.relativedelta.relativedelta(years=plan.validity)
                else:
                    end_date = None 

                # Set start_date and end_date
                prop_instance.start_date = start_date
                prop_instance.end_date = end_date
            elif prop_instance.expired:
                prop_instance.end_date = None
            prop_instance.save()

            msg = "Successfully updated."
            if option_type == 'rejected':
                send_ad_reject_mail(request, prop_instance.user.email)
            else:
                send_ad_approve_mail(request, prop_instance.user.email, prop_instance)

        msg = "Successfully updated."
    else:
        msg = "Approved set to False for all."

    return JsonResponse({"msg": msg}, safe=False)


def set_approved_general(request):
    approved_ids = request.GET.getlist('approved_ids[]')
    option_type = request.GET.get('option_type')
    if approved_ids:
        prop_instances = GeneralSubCategory.objects.filter(id__in=approved_ids)
        
        for prop_instance in prop_instances:
            # Set approved to True
            approved_status = True
            if option_type == 'rejected':
                approved_status = False
                prop_instance.expired = True
            prop_instance.approved = approved_status

            # Set start date to now
            start_date = timezone.now().date()

            # Get associated plan details
            transaction = prop_instance.transaction
            if transaction and transaction.plan_id and not prop_instance.expired:
                plan = transaction.plan_id
                if plan.validity_type == "Days":
                    end_date = start_date + timedelta(days=plan.validity)
                elif plan.validity_type == "Weeks":
                    end_date = start_date + timedelta(weeks=plan.validity)
                elif plan.validity_type == "Month":
                    end_date = start_date + dateutil.relativedelta.relativedelta(months=plan.validity)
                elif plan.validity_type == "Year":
                    end_date = start_date + dateutil.relativedelta.relativedelta(years=plan.validity)
                else:
                    end_date = None 

                # Set start_date and end_date
                prop_instance.start_date = start_date
                prop_instance.end_date = end_date
            elif prop_instance.expired:
                prop_instance.end_date = None
            prop_instance.save()

            msg = "Successfully updated."
            if option_type == 'rejected':
                send_ad_reject_mail(request, prop_instance.user.email)
            else:
                send_ad_approve_mail(request, prop_instance.user.email, prop_instance)

        msg = "Successfully updated."
    else:
        msg = "Approved set to False for all."

    return JsonResponse({"msg": msg}, safe=False)


def set_approved_job(request):
  
    approved_ids = request.GET.getlist('approved_ids[]')
    option_type = request.GET.get('option_type')
    if approved_ids:
        prop_instances = JobsSubCategory.objects.filter(id__in=approved_ids)
        
        for prop_instance in prop_instances:
            # Set approved to True
            approved_status = True
            if option_type == 'rejected':
                approved_status = False
                prop_instance.expired = True
            prop_instance.approved = approved_status

            # Set start date to now
            start_date = timezone.now().date()

            # Get associated plan details
            transaction = prop_instance.transaction
            if transaction and transaction.plan_id and not prop_instance.expired:
                plan = transaction.plan_id
                if plan.validity_type == "Days":
                    end_date = start_date + timedelta(days=plan.validity)
                elif plan.validity_type == "Weeks":
                    end_date = start_date + timedelta(weeks=plan.validity)
                elif plan.validity_type == "Month":
                    end_date = start_date + dateutil.relativedelta.relativedelta(months=plan.validity)
                elif plan.validity_type == "Year":
                    end_date = start_date + dateutil.relativedelta.relativedelta(years=plan.validity)
                else:
                    end_date = None 

                # Set start_date and end_date
                prop_instance.start_date = start_date
                prop_instance.end_date = end_date
            elif prop_instance.expired:
                prop_instance.end_date = None
            prop_instance.save()

            msg = "Successfully updated."
            if option_type == 'rejected':
                send_ad_reject_mail(request, prop_instance.user.email)
            else:
                send_ad_approve_mail(request, prop_instance.user.email, prop_instance)

        msg = "Successfully updated."
    else:
        msg = "Approved set to False for all."

    return JsonResponse({"msg": msg}, safe=False)

def set_approved_company(request):
    approved_ids = request.GET.getlist('approved_ids[]')
    option_type = request.GET.get('option_type')
    if approved_ids:
        prop_instances = CompanySubCategory.objects.filter(id__in=approved_ids)
        
        for prop_instance in prop_instances:
            # Set approved to True
            approved_status = True
            if option_type == 'rejected':
                approved_status = False
                prop_instance.expired = True
            prop_instance.approved = approved_status

            # Set start date to now
            start_date = timezone.now().date()

            # Get associated plan details
            transaction = prop_instance.transaction
            if transaction and transaction.plan_id and not prop_instance.expired:
                plan = transaction.plan_id
                if plan.validity_type == "Days":
                    end_date = start_date + timedelta(days=plan.validity)
                elif plan.validity_type == "Weeks":
                    end_date = start_date + timedelta(weeks=plan.validity)
                elif plan.validity_type == "Month":
                    end_date = start_date + dateutil.relativedelta.relativedelta(months=plan.validity)
                elif plan.validity_type == "Year":
                    end_date = start_date + dateutil.relativedelta.relativedelta(years=plan.validity)
                else:
                    end_date = None 

                # Set start_date and end_date
                prop_instance.start_date = start_date
                prop_instance.end_date = end_date
            elif prop_instance.expired:
                prop_instance.end_date = None
            prop_instance.save()

            msg = "Successfully updated."
            if option_type == 'rejected':
                send_ad_reject_mail(request, prop_instance.user.email)
            else:
                send_ad_approve_mail(request, prop_instance.user.email, prop_instance)

        msg = "Successfully updated."
    else:
        msg = "Approved set to False for all."

    return JsonResponse({"msg": msg}, safe=False)


def set_approved_article(request):
   
    approved_ids = request.GET.getlist('approved_ids[]')
    option_type = request.GET.get('option_type')
    if approved_ids:
        prop_instances = ArticleSubCategory.objects.filter(id__in=approved_ids)
        
        for prop_instance in prop_instances:
            # Set approved to True
            approved_status = True
            if option_type == 'rejected':
                approved_status = False
                prop_instance.expired = True
            prop_instance.approved = approved_status

            # Set start date to now
            start_date = timezone.now().date()

            # Get associated plan details
            transaction = prop_instance.transaction
            if transaction and transaction.plan_id and not prop_instance.expired:
                plan = transaction.plan_id
                if plan.validity_type == "Days":
                    end_date = start_date + timedelta(days=plan.validity)
                elif plan.validity_type == "Weeks":
                    end_date = start_date + timedelta(weeks=plan.validity)
                elif plan.validity_type == "Month":
                    end_date = start_date + dateutil.relativedelta.relativedelta(months=plan.validity)
                elif plan.validity_type == "Year":
                    end_date = start_date + dateutil.relativedelta.relativedelta(years=plan.validity)
                else:
                    end_date = None 

                # Set start_date and end_date
                prop_instance.start_date = start_date
                prop_instance.end_date = end_date
            elif prop_instance.expired:
                prop_instance.end_date = None
            prop_instance.save()

            msg = "Successfully updated."
            if option_type == 'rejected':
                send_ad_reject_mail(request, prop_instance.user.email)
            else:
                send_ad_approve_mail(request, prop_instance.user.email, prop_instance)

        msg = "Successfully updated."
    else:
        msg = "Approved set to False for all."

    return JsonResponse({"msg": msg}, safe=False)


def contact_us_view(request):
    return render(request, "users/features/contactUs_Page.html") 
 