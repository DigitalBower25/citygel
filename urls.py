from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.authentication.views import HomeViewPage
from features.views import (privacy_policy_page, term_condition_page, term_condition_page, emirate_home_page,
                            cookie_policy_page, article_detail_page, cancellation_policy_page, contact_us_view,
                            emirate_category_page, CategoryDetailView)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeViewPage.as_view(), name="user_home"),
    path('user/', include("users.urls")),
    path('user-auth/', include("users.authentication.urls")),
    path('feature/', include("features.urls")),
    path('', include("users.sup-admin.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# other urls add
urlpatterns += [
    path("privacy-policy", privacy_policy_page, name="privacy_policy"),
    path("term-and-condition", term_condition_page, name="term_condition"),
    path("cookie-policy", cookie_policy_page, name="cookie_policy"),
    path("cancellation-policy", cancellation_policy_page, name="cancellation_policy"),
    path("contact", contact_us_view, name="contact_us_view"),
]

# change urls
urlpatterns += [
    path("<str:country_code>/<str:state_id>/", emirate_category_page, name="emirate_category_page"),
    path("<str:country_slug>/<str:state_slug>/article/<str:article_id>/", article_detail_page, name="article_detail_page"),
    path("<str:country_id>/<str:state_id>/<str:category_id>/", emirate_home_page, name="emirate_home_page"),

    path("<str:country_code>/<str:state_id>/<str:ad_type>/<str:detail_name>/", CategoryDetailView.as_view(),
         name="category_detail_page"),
]