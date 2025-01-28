import datetime
from django.utils import timezone
from datetime import timedelta
import dateutil.relativedelta
from .models import *
# from django.core.mail import send_mail
from django.core.mail import EmailMessage
import os
import threading
from django.template.loader import get_template
from urllib.parse import urljoin
from django.templatetags.static import static
from CityGel.settings import BASE_DIR


def sub_category_count(category, subcategory_model):
    return subcategory_model.objects.filter(category__category_name=category).count()


def sub_category_context_model(ad_type):
    model_objects = {
        "Properties": PropertiesSubCategory,
        "Motor": MotorSubCategory,
        "General": GeneralSubCategory,
        "Jobs": JobsSubCategory,
        "Company": CompanySubCategory,
        "Article": ArticleSubCategory,
    }
    return model_objects[ad_type]


class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMessage(
            self.subject,
            self.html_content,
            os.environ.get("EMAIL_HOST_USER"),
            self.recipient_list,
        )
        msg.content_subtype = "html"
        msg.send()
        print("email sent!")


def send_html_mail(subject, html_content, recipient_list):
    EmailThread(subject, html_content, recipient_list).start()


def send_mail_expired_ad_cron():
    path = os.path.join(BASE_DIR)
    now = datetime.datetime.today()
    email_list = []

    subcategories = [
        PropertiesSubCategory,
        CompanySubCategory,
        JobsSubCategory,
        GeneralSubCategory,
        MotorSubCategory,
        ArticleSubCategory
    ]

    for subcategory in subcategories:
        expired_entries = subcategory.objects.select_related().filter(end_date__lt=now, approved=True, expired=False)
        for entry in expired_entries:
            entry.expired = True
            entry.save()
            email_list.append(entry.user.email)

    subject = "Your Ad Has Expired"
    context = {
        "user_name": "User",
        "logo": urljoin("https://citygel.com/", static('design/images/logo.png')),
    }
    template = get_template(f"{path}/templates/email/ad_expired_email.html")
    rendered_email = template.render(context)
    send_html_mail(subject, rendered_email, email_list)

    pass


def send_mail_approve_ad_cron():
    path = os.path.join(BASE_DIR)

    now = timezone.now()
    time_24_hours_ago = now - datetime.timedelta(hours=24)

    subcategories = [
        PropertiesSubCategory,
        CompanySubCategory,
        JobsSubCategory,
        GeneralSubCategory,
        MotorSubCategory,
        ArticleSubCategory
    ]

    for subcategory in subcategories:
        unapprove_entries = subcategory.objects.select_related().filter(end_date=None,
                                                                        approved=False, expired=False,
                                                                        created_at__gte=time_24_hours_ago, payment_status=True)
        print(unapprove_entries.values('end_date'), "unapprove_entries", subcategory)
        for entry in unapprove_entries:
            entry.approved = True

            transaction = entry.transaction
            if transaction and transaction.plan_id and not entry.expired:
                start_date = timezone.now().date()
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
                entry.start_date = start_date
                entry.end_date = end_date
            elif entry.expired:
                entry.end_date = None

            entry.save()

            subject = "Your Ad is Now Live on Citygel!"
            context = {
                "user_name": entry.user.full_name,
                "logo": urljoin("https://citygel.com/", static('design/images/logo.png')),
                "item_link": f"https://citygel.com/feature/category-detail/{entry.category.ad_type}/{entry.id}/"
            }
            template = get_template(f"{path}/templates/email/ad_approve_email.html")
            rendered_email = template.render(context)
            send_html_mail(subject, rendered_email, [entry.user.email])

    pass



