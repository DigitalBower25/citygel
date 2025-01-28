from django.contrib import admin
from .models import *

@admin.register(State)
class StateAdminView(admin.ModelAdmin):
    list_display = ("country", "state", "slug")
    search_fields = ("state",)

@admin.register(City)
class CityAdminView(admin.ModelAdmin):
    list_display = ("state", "city")
    search_fields = ("city",)

@admin.register(Category)
class CategoryAdminView(admin.ModelAdmin):
    list_display = ("ad_type", "category_name", "slug", "image")
    search_fields = ("category_name",)


@admin.register(SubCategoryModel)
class SubCategoryModelAdminView(admin.ModelAdmin):
    list_display = ("category", "sub_category", )
    search_fields = ("category", "sub_category")


@admin.register(SubCategoryType)
class SubCategoryTypeAdminView(admin.ModelAdmin):
    list_display = ("sub_category", "type_name",)
    search_fields = ("sub_category", "type_name")


@admin.register(TagsModel)
class TagsModelAdminView(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(PlanFeaturesModel)
class PlanFeaturesModelAdminView(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(PropertiesSubCategory)
class PropertiesSubCategoryAdminView(admin.ModelAdmin):
    list_display = ("category", "user", "sub_category", "slug", "type", "ad_title", "created_at", 'payment_status')
    search_fields = ("category", "sub_category", "type", "ad_title", 'approved', 'payment_status')
    list_filter = ("category", "sub_category", "type", 'approved', 'expired', 'payment_status')
    list_editable = ('payment_status',)


@admin.register(MotorBrand)
class MotorBrandAdminView(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(MotorModel)
class MotorModelAdminView(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(MotorSubCategory)
class MotorSubCategoryAdminView(admin.ModelAdmin):
    list_display = ("category", "sub_category",  "slug", "type", "user", "ad_title", "created_at", "payment_status")
    search_fields = ("category", "sub_category", "type", "ad_title", 'payment_status', 'approved')
    list_filter = ("category", "sub_category", "type", 'approved', 'expired', 'payment_status')
    list_editable = ('payment_status',)


@admin.register(GeneralSubCategory)
class GeneralSubCategoryAdminView(admin.ModelAdmin):
    list_display = ("category", "sub_category", "slug", "type", "user", "ad_title", "created_at", "payment_status")
    search_fields = ("category", "sub_category", "type", "ad_title", 'approved', 'payment_status')
    list_filter = ("category", "sub_category", "type",'approved', 'expired', 'payment_status')
    list_editable = ('payment_status',)


@admin.register(JobsSubCategory)
class JobsSubCategoryAdminView(admin.ModelAdmin):
    list_display = ("category", "sub_category", "slug", "type", "user", "ad_title", "created_at", "payment_status")
    search_fields = ("category", "sub_category", "type", "ad_title", 'approved', 'payment_status')
    list_filter = ("category", "sub_category", "type", 'approved', 'expired', 'payment_status')
    list_editable = ('payment_status',)


@admin.register(CompanySubCategory)
class CompanySubCategoryAdminView(admin.ModelAdmin):
    list_display = ("category", "sub_category", "slug", "type", "user", "ad_title", "created_at", "payment_status")
    search_fields = ("category", "sub_category", "type", "ad_title", 'approved', 'payment_status')
    list_filter = ("category", "sub_category", "type", 'approved', 'expired', 'payment_status')
    list_editable = ('payment_status',)


@admin.register(ArticleSubCategory)
class ArticleSubCategoryAdminView(admin.ModelAdmin):
    list_display = ("category", "sub_category", "slug", "type", "user", "ad_title", "created_at", "payment_status")
    search_fields = ("category", "sub_category", "type", "ad_title", 'approved', 'payment_status')
    list_filter = ("category", "sub_category", "type", 'approved', 'expired', 'payment_status')
    list_editable = ('payment_status',)


@admin.register(PlanCreation)
class PlanCreationAdminView(admin.ModelAdmin):
    list_display = ("validity_type", "validity", "price", "plan_title")


@admin.register(SubCategoryImages)
class SubCategoryImagesAdminView(admin.ModelAdmin):
    list_display = ("properties_sub_category", "motor_sub_category", "general_sub_category", "articles_sub_category", "images")


@admin.register(EnquiryModel)
class EnquiryModelAdminView(admin.ModelAdmin):
    list_display = ("ad_user", "sub_category", "ad_title", "name", "phone_number")


@admin.register(TransactionModel)
class TransactionModelAdminView(admin.ModelAdmin):
    list_display = ("user", "amount", "status", "created_at")
    search_fields = ("amount", "user")


@admin.register(FooterBanners)
class FooterBannersAdminView(admin.ModelAdmin):
    list_display = ("type", "title", "description")


@admin.register(AdBanner)
class AdBannerAdminView(admin.ModelAdmin):
    list_display = ("types", "ad_side", "image")
    search_fields = ("types", "ad_side")

@admin.register(FeatureAds)
class FeatureAdsAdminView(admin.ModelAdmin):
    #list_display = ("types", "ad_side", "image")
    search_fields = ("types", "ad_side")

admin.site.register(EnquiryTypeModel)
