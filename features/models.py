from django.db import models
from users.managers import BaseModel
from users.models import CountryCode, UserModel,UsersFeaturedAds
from PIL import Image
from django.core.exceptions import ValidationError
from users.models import LowercaseEmailField
from django.core.validators import MinValueValidator, MaxValueValidator
from ckeditor.fields import RichTextField
from django.core.files.uploadedfile import InMemoryUploadedFile
import io
import sys
from django.utils.text import slugify


class State(BaseModel):
    country = models.ForeignKey(CountryCode, on_delete=models.CASCADE)
    state = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True, help_text="please blank field sumit")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.state)
            original_slug = self.slug
            counter = 1
            while State.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super(State, self).save(*args, **kwargs)

    def __str__(self):
        # return f"{self.state} ({self.country.name})"
        return f"{self.state} "


class City(BaseModel):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    city = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.city} "


def validate_image(value):
    max_width = 74
    max_height = 74

    image = Image.open(value)
    width, height = image.size

    if width != max_width or height != max_height:
        raise ValidationError(
            f"The image dimensions should be {max_width}x{max_height} pixels for {value.instance} banner."
        )


class Category(BaseModel):
    state = models.ManyToManyField(State, blank=True)
    AD_TYPE_CHOICE = {
        ("Properties", "Properties"),
        ("Motor", "Motor"),
        ("General", "General"),
        ("Jobs", "Jobs"),
        ("Company", "Company"),
        ("Article", "Article"),
    }
    ad_type = models.CharField(max_length=30, choices=AD_TYPE_CHOICE)
    category_name = models.CharField(max_length=30)
    image = models.ImageField(upload_to="category-img", validators=[validate_image])
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True, help_text="please blank field sumit")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.category_name)
            original_slug = self.slug
            counter = 1
            while Category.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.category_name} ({self.ad_type})"

    class Meta:
        unique_together = (
            "ad_type",
            "category_name",
        )


class SubCategoryModel(BaseModel):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="sub_category_model"
    )
    sub_category = models.CharField(max_length=30)
    # image = models.ImageField(upload_to="sub-category-img", validators=[validate_image])

    def __str__(self):
        return f"{self.sub_category} ({self.category.category_name})"

    class Meta:
        unique_together = (
            "category",
            "sub_category",
        )

    def sub_category_type(self):
        instance = SubCategoryType.objects.filter(sub_category=self.id)
        return instance


class SubCategoryType(BaseModel):
    sub_category = models.ForeignKey(SubCategoryModel, on_delete=models.CASCADE)
    type_name = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.type_name}"


class FuelModel(BaseModel):
    sub_category = models.ForeignKey(SubCategoryModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ListedByModel(BaseModel):
    sub_category = models.ForeignKey(SubCategoryModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class TransmissionModel(BaseModel):
    sub_category = models.ForeignKey(SubCategoryModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class EnquiryTypeModel(BaseModel):
    sub_category = models.ForeignKey(SubCategoryModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.capitalize()
        super().save(*args, **kwargs)


class RoomsModel(BaseModel):
    sub_category = models.ForeignKey(SubCategoryModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class FurnitureModel(BaseModel):
    sub_category = models.ForeignKey(SubCategoryModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ConstructionTypeModel(BaseModel):
    sub_category = models.ForeignKey(SubCategoryModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CarParkingModel(BaseModel):
    sub_category = models.ForeignKey(SubCategoryModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class AreaUnitModel(BaseModel):
    sub_category = models.ForeignKey(SubCategoryModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class TagsModel(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class PlanFeaturesModel(BaseModel):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class PlanCreation(BaseModel):
    PLAN_CHOICES = [
        ("Days", "Days"),
        ("Weeks", "Weeks"),
        ("Month", "Month"),
        ("Year", "Year"),
    ]
    PLAN_TYPE = [("Normal", "Normal"), ("Most Popular", "Most Popular")]
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    validity_type = models.CharField(max_length=12, choices=PLAN_CHOICES)
    plan_type = models.CharField(max_length=13, choices=PLAN_TYPE)
    validity = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        help_text="How many days/month/year",
    )
    price = models.IntegerField()
    plan_title = models.CharField(max_length=25)
    plan_feature = models.ManyToManyField(PlanFeaturesModel)
    description = models.CharField(max_length=250)


class TransactionModel(BaseModel):
    plan_id = models.ForeignKey(
        PlanCreation, on_delete=models.SET_NULL, null=True, blank=True
    )
    user = models.ForeignKey(
        UserModel, on_delete=models.SET_NULL, null=True, blank=True
    )
    amount = models.FloatField()
    status = models.CharField(
        max_length=10,
        choices={("Pending", "Pending"), ("Failed", "Failed"), ("Success", "Success"), ("InComplete", "InComplete")},
    )
    transaction_detail = models.JSONField()
    transaction_secret = models.TextField()
    transaction_id = models.TextField()

    def __str__(self):
        return f"Transaction {self.id} - {self.status}"


class PropertiesSubCategory(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(
        SubCategoryModel, on_delete=models.SET_NULL, null=True
    )
    type = models.ForeignKey(SubCategoryType, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(TagsModel)
    rooms = models.ForeignKey(RoomsModel, on_delete=models.SET_NULL, null=True)
    furniture = models.ForeignKey(FurnitureModel, on_delete=models.SET_NULL, null=True)
    construction_type = models.ForeignKey(
        ConstructionTypeModel, on_delete=models.SET_NULL, null=True
    )
    listed_by = models.ForeignKey(
        ListedByModel,
        on_delete=models.SET_NULL,
        related_name="listed",
        null=True,
        blank=True,
    )
    area = models.CharField(max_length=150)
    area_unit = models.ForeignKey(AreaUnitModel, on_delete=models.SET_NULL, null=True)
    car_parking = models.ForeignKey(
        CarParkingModel, on_delete=models.SET_NULL, null=True
    )
    ad_title = models.CharField(max_length=25)
    description = models.TextField()
    # description =RichTextField()
    total_price = models.FloatField()
    country = models.ForeignKey(CountryCode, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    enquiry_type = models.ForeignKey(
        EnquiryTypeModel,
        on_delete=models.SET_NULL,
        related_name="enquiry",
        null=True,
        blank=True,
    )
    approved = models.BooleanField(default=False)
    map_link = models.URLField(max_length=2000, verbose_name="Google Map Link")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    transaction = models.ForeignKey(
        TransactionModel, on_delete=models.SET_NULL, null=True
    )
    expired = models.BooleanField(default=False)
    payment_status = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True, help_text="please blank field sumit")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.ad_title)
            original_slug = self.slug
            counter = 1
            while PropertiesSubCategory.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super(PropertiesSubCategory, self).save(*args, **kwargs)

    def item_images(self):
        instance = SubCategoryImages.objects.filter(properties_sub_category=self.id)
        return instance if instance else None


class MotorBrand(BaseModel):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class MotorModel(BaseModel):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class MotorSubCategory(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(
        SubCategoryModel, on_delete=models.SET_NULL, null=True
    )
    type = models.ForeignKey(SubCategoryType, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(TagsModel)
    brand = models.ForeignKey(MotorBrand, on_delete=models.SET_NULL, null=True)
    model = models.ForeignKey(MotorModel, on_delete=models.SET_NULL, null=True)
    year = models.IntegerField()
    fuel = models.ForeignKey(
        FuelModel, on_delete=models.SET_NULL, related_name="Fuel", null=True
    )
    listed_by = models.ForeignKey(
        ListedByModel,
        on_delete=models.SET_NULL,
        related_name="listed_By",
        null=True,
        blank=True,
    )
    transmission = models.ForeignKey(
        TransmissionModel,
        on_delete=models.SET_NULL,
        related_name="Transmission",
        null=True,
    )
    km_driven = models.IntegerField()
    no_of_owners = models.IntegerField()
    ad_title = models.CharField(max_length=25)
    description = models.TextField()
    total_price = models.FloatField()
    country = models.ForeignKey(CountryCode, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    enquiry_type = models.ForeignKey(
        EnquiryTypeModel,
        on_delete=models.SET_NULL,
        related_name="enq",
        null=True,
        blank=True,
    )
    approved = models.BooleanField(default=False)
    map_link = models.URLField(max_length=2000)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    transaction = models.ForeignKey(
        TransactionModel, on_delete=models.SET_NULL, null=True
    )
    expired = models.BooleanField(default=False)
    payment_status = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True, help_text="please blank field sumit")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.ad_title)
            original_slug = self.slug
            counter = 1
            while MotorSubCategory.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super(MotorSubCategory, self).save(*args, **kwargs)

    def item_images(self):
        instance = SubCategoryImages.objects.filter(motor_sub_category=self.id)
        return instance if instance else None


class GeneralSubCategory(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(
        SubCategoryModel, on_delete=models.SET_NULL, null=True
    )
    type = models.ForeignKey(SubCategoryType, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(TagsModel)
    ad_title = models.CharField(max_length=25)
    description = models.TextField()
    total_price = models.FloatField()
    country = models.ForeignKey(CountryCode, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    enquiry_type = models.ForeignKey(
        EnquiryTypeModel,
        on_delete=models.SET_NULL,
        related_name="enquiryType",
        null=True,
        blank=True,
    )
    approved = models.BooleanField(default=False)
    # map_link = models.URLField(max_length=2000)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    transaction = models.ForeignKey(
        TransactionModel, on_delete=models.SET_NULL, null=True
    )
    expired = models.BooleanField(default=False)
    payment_status = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True, help_text="please blank field sumit")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.ad_title)
            original_slug = self.slug
            counter = 1
            while GeneralSubCategory.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super(GeneralSubCategory, self).save(*args, **kwargs)

    def item_images(self):
        instance = SubCategoryImages.objects.filter(general_sub_category=self.id)
        return instance if instance else None


class JobsSubCategory(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(
        SubCategoryModel, on_delete=models.SET_NULL, null=True
    )
    type = models.ForeignKey(SubCategoryType, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(TagsModel)
    ad_title = models.CharField(max_length=25)
    description = models.TextField()
    total_price = models.FloatField(verbose_name="Salary")
    country = models.ForeignKey(CountryCode, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    enquiry_type = models.ForeignKey(
        EnquiryTypeModel,
        on_delete=models.SET_NULL,
        related_name="EnquiryType",
        null=True,
        blank=True,
    )
    enquiry_link = models.CharField(max_length=100, null=True, blank=True)
    approved = models.BooleanField(default=False)
    # map_link = models.URLField(max_length=2000)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    transaction = models.ForeignKey(
        TransactionModel, on_delete=models.SET_NULL, null=True
    )
    expired = models.BooleanField(default=False)
    payment_status = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True, help_text="please blank field sumit")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.ad_title)
            original_slug = self.slug
            counter = 1
            while JobsSubCategory.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super(JobsSubCategory, self).save(*args, **kwargs)


class CompanySubCategory(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(
        SubCategoryModel, on_delete=models.SET_NULL, null=True
    )
    type = models.ForeignKey(SubCategoryType, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(TagsModel)
    ad_title = models.CharField(max_length=25)
    description = models.TextField()
    total_price = models.FloatField(null=True, blank=True)
    website = models.CharField(max_length=150)
    country = models.ForeignKey(CountryCode, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    enquiry_type = models.ForeignKey(
        EnquiryTypeModel,
        on_delete=models.SET_NULL,
        related_name="Enquirytype",
        null=True,
        blank=True,
    )
    approved = models.BooleanField(default=False)
    # map_link = models.URLField(max_length=2000)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    transaction = models.ForeignKey(
        TransactionModel, on_delete=models.SET_NULL, null=True
    )
    expired = models.BooleanField(default=False)
    payment_status = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True, help_text="please blank field sumit")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.ad_title)
            original_slug = self.slug
            counter = 1
            while CompanySubCategory.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super(CompanySubCategory, self).save(*args, **kwargs)


class ArticleSubCategory(BaseModel):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(
        SubCategoryModel, on_delete=models.SET_NULL, null=True
    )
    type = models.ForeignKey(SubCategoryType, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(TagsModel)
    ad_title = models.CharField(max_length=25)
    # description = models.TextField()
    description = RichTextField()
    total_price = models.FloatField(null=True, blank=True)
    website = models.CharField(max_length=150)
    country = models.ForeignKey(CountryCode, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    # enquiry_type = models.ForeignKey(
    #     EnquiryTypeModel,
    #     on_delete=models.SET_NULL,
    #     related_name="Enq_Type",
    #     null=True,
    #     blank=True,
    # )
    approved = models.BooleanField(default=False)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    transaction = models.ForeignKey(
        TransactionModel, on_delete=models.SET_NULL, null=True
    )
    expired = models.BooleanField(default=False)
    payment_status = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True, help_text="please blank field sumit")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.ad_title)
            original_slug = self.slug
            counter = 1
            while ArticleSubCategory.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super(ArticleSubCategory, self).save(*args, **kwargs)

    def item_images(self):
        instance = SubCategoryImages.objects.filter(articles_sub_category=self.id)
        return instance if instance else None


# Portrait images are not accepted function
def validate_landscape(image):
    img = Image.open(image)
    width, height = img.size

    if height > width:
        raise ValidationError(
            "Portrait images are not accepted as they will break the design. Please upload a landscape image."
        )

    # Resize to a standard rectangle (landscape) size if necessary
    new_width = max(width, height)  # Ensures it's a landscape
    new_height = int(new_width * 3 / 4)

    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    if img.mode == 'RGBA':
        img = img.convert('RGB')

    # Save the image back to the file
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=85)
    output.seek(0)

    # Replace the original image with the resized one
    image.file = InMemoryUploadedFile(
        output, 'ImageField', f"{image.name.split('.')[0]}.jpg", 'image/jpeg',
        sys.getsizeof(output), None
    )

    return image


class SubCategoryImages(BaseModel):
    properties_sub_category = models.ForeignKey(
        PropertiesSubCategory, on_delete=models.CASCADE, null=True, blank=True
    )
    motor_sub_category = models.ForeignKey(
        MotorSubCategory, on_delete=models.CASCADE, null=True, blank=True
    )
    general_sub_category = models.ForeignKey(
        GeneralSubCategory, on_delete=models.CASCADE, null=True, blank=True
    )
    articles_sub_category = models.ForeignKey(
        ArticleSubCategory, on_delete=models.CASCADE, null=True, blank=True
    )
    # images = models.ImageField(upload_to="uploaded-image")
    images = models.ImageField(
        upload_to="uploaded-image/", validators=[validate_landscape]
    )


class EnquiryModel(BaseModel):
    ad_user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategoryModel, on_delete=models.CASCADE)
    ad_title = models.CharField(max_length=160)
    name = models.CharField(max_length=100, verbose_name="Full Name")
    email = LowercaseEmailField(verbose_name="Email Id")
    phone_number = models.CharField(
        verbose_name="Contact No", max_length=15, null=True, blank=True
    )
    message = models.TextField()
    cv = models.FileField(upload_to="cv", null=True, blank=True)


def validate_footer_image(value):
    # Access the model instance via `value.instance`
    instance = value.instance

    # Determine expected dimensions based on the instance's `type` field
    if instance.type == "desktop":
        min_width, max_width = 1200, 1381
        min_height, max_height = 300, 392
    elif instance.type == "mobile":
        min_width, max_width = 320, 375
        min_height, max_height = 120, 155
    else:
        raise ValidationError(f"Invalid type: {instance.type}")

    # Open the image and validate dimensions
    try:
        image = Image.open(value)
        actual_width, actual_height = image.size
    except IOError:
        raise ValidationError(f"Cannot open the image file {value.name}.")

    if not (min_width <= actual_width <= max_width) or not (
        min_height <= actual_height <= max_height
    ):
        raise ValidationError(
            f"For type '{instance.type}', the image dimensions should be within "
            f"{min_width}-{max_width} pixels width and {min_height}-{max_height} pixels height. "
            f"Got {actual_width}x{actual_height} pixels."
        )


class FooterBanners(BaseModel):
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    type = models.CharField(
        max_length=10, choices={("mobile", "mobile"), ("desktop", "desktop")}
    )
    image = models.ImageField(
        upload_to="footer-banner", validators=[validate_footer_image]
    )
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=150)
    button_link = models.URLField()


def validate_ads_image(value):
    # Access the model instance via `value.instance`
    instance = value.instance

    # Determine expected dimensions based on the instance's `type` field
    if instance.ad_side == "top":
        if instance.types == "desktop":
            min_width, max_width = 1200, 1381
            min_height, max_height = 300, 392
        elif instance.types == "mobile":
            min_width, max_width = 320, 375
            min_height, max_height = 120, 155
        else:
            raise ValidationError(f"Invalid type: {instance.types}")
    else:
        if instance.types == "desktop":
            min_width, max_width = 300, 392
            min_height, max_height = 1200, 1381
        elif instance.types == "mobile":
            min_width, max_width = 320, 375
            min_height, max_height = 120, 155
        else:
            raise ValidationError(f"Invalid type: {instance.types}")

    # Open the image and validate dimensions
    try:
        image = Image.open(value)
        actual_width, actual_height = image.size
    except IOError:
        raise ValidationError(f"Cannot open the image file {value.name}.")

    if not (min_width <= actual_width <= max_width) or not (
        min_height <= actual_height <= max_height
    ):
        raise ValidationError(
            f"For type '{instance.types}', the image dimensions should be within "
            f"{min_width}-{max_width} pixels width and {min_height}-{max_height} pixels height. "
            f"Got {actual_width}x{actual_height} pixels."
        )


class AdBanner(BaseModel):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="CATEGORY"
    )
    sub_category = models.ForeignKey(
        SubCategoryModel, on_delete=models.CASCADE, related_name="SUB_CATEGORY"
    )
    page_type = models.CharField(
        max_length=16,
        choices={
            ("detail_page", "detail_page"),
            ("listing_page", "listing_page"),
            ("article_page", "article_page"),
            ("ad_creation_page", "ad_creation_page"),
        },
    )
    types = models.CharField(
        max_length=10, choices={("mobile", "mobile"), ("desktop", "desktop")}
    )
    ad_side = models.CharField(
        max_length=10,
        choices={("top", "top"), ("bottom", "bottom")},
        null=True,
        blank=True,
    )
    image = models.ImageField(upload_to="ad-banner", validators=[validate_ads_image])
    hyper_link = models.URLField()

class FeatureAds(BaseModel):
    image = models.ImageField(upload_to="ad-features", validators=[validate_ads_image])
    title = models.CharField(max_length=300)
    description = models.CharField(max_length=500)
    priceCode = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    price = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100)

    


