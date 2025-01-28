from django.forms import ModelForm
from django import forms
from .models import *
from users.models import UserModel


class PropertiesAdForm(ModelForm):
    class Meta:
        model = PropertiesSubCategory
        fields = "__all__"
        exclude = ("sub_category", "category", "user", "approved", "transaction", "start_date", "end_date", "expired",
                   "payment_status", "slug")

    def __init__(self, *args, **kwargs):
        sub_category = kwargs.pop('sub_category', None)
        super().__init__(*args, **kwargs)
        self.fields['enquiry_type'].required = True
        
        self.fields['tags'].widget = forms.CheckboxSelectMultiple()
        if sub_category:
            sub_category_type_queryset = SubCategoryType.objects.filter(sub_category=sub_category)
            self.fields['type'].queryset = sub_category_type_queryset

            if sub_category_type_queryset:
                category_queryset = TagsModel.objects.filter(category=sub_category_type_queryset.first().sub_category.category)
                self.fields['tags'].queryset = category_queryset
                self.fields['enquiry_type'].queryset = EnquiryTypeModel.objects.filter(sub_category=sub_category)
                self.fields['listed_by'].queryset = ListedByModel.objects.filter(sub_category=sub_category)
                self.fields['rooms'].queryset = RoomsModel.objects.filter(sub_category=sub_category)
                self.fields['furniture'].queryset = FurnitureModel.objects.filter(sub_category=sub_category)
                self.fields['construction_type'].queryset = ConstructionTypeModel.objects.filter(sub_category=sub_category)
                self.fields['car_parking'].queryset = CarParkingModel.objects.filter(sub_category=sub_category)
                self.fields['area_unit'].queryset = AreaUnitModel.objects.filter(sub_category=sub_category)
            else:
                self.fields['tags'].queryset = TagsModel.objects.none()
                self.fields['enquiry_type'].queryset = EnquiryTypeModel.objects.none()
                self.fields['listed_by'].queryset = ListedByModel.objects.none()
                self.fields['rooms'].queryset = RoomsModel.objects.none()
                self.fields['furniture'].queryset = FurnitureModel.objects.none()
                self.fields['construction_type'].queryset = ConstructionTypeModel.objects.none()
                self.fields['car_parking'].queryset = CarParkingModel.objects.none()
                self.fields['area_unit'].queryset = AreaUnitModel.objects.none()
        else:
            self.fields['type'].queryset = SubCategoryType.objects.none()
            self.fields['tags'].queryset = TagsModel.objects.none()
            self.fields['enquiry_type'].queryset = EnquiryTypeModel.objects.none()
            self.fields['listed_by'].queryset = ListedByModel.objects.none()
            self.fields['rooms'].queryset = RoomsModel.objects.none()
            self.fields['furniture'].queryset = FurnitureModel.objects.none()
            self.fields['construction_type'].queryset = ConstructionTypeModel.objects.none()
            self.fields['car_parking'].queryset = CarParkingModel.objects.none()
            self.fields['area_unit'].queryset = AreaUnitModel.objects.none()

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if len(tags) == 0:
            raise forms.ValidationError("Please select atleast 1 tags")
        return tags
    


class MotorAdForm(ModelForm):
    class Meta:
        model = MotorSubCategory
        fields = "__all__"
        exclude = ("sub_category", "category", "user", "approved", "transaction", "start_date", "end_date", "expired",
                   "payment_status", "slug")

    def __init__(self, *args, **kwargs):
        sub_category = kwargs.pop('sub_category', None)
        super().__init__(*args, **kwargs)
        self.fields['enquiry_type'].required = True

        if sub_category:
            sub_category_type_queryset = SubCategoryType.objects.filter(sub_category=sub_category)
            self.fields['type'].queryset = sub_category_type_queryset
            
            self.fields['tags'].widget = forms.CheckboxSelectMultiple()

            if sub_category_type_queryset:
                category_queryset = TagsModel.objects.filter(
                    category=sub_category_type_queryset.first().sub_category.category)
                self.fields['tags'].queryset = category_queryset
                self.fields['listed_by'].queryset = ListedByModel.objects.filter(sub_category=sub_category)
                self.fields['fuel'].queryset = FuelModel.objects.filter(sub_category=sub_category)
                self.fields['transmission'].queryset = TransmissionModel.objects.filter(sub_category=sub_category)
                self.fields['enquiry_type'].queryset = EnquiryTypeModel.objects.filter(sub_category=sub_category)
            else:
                self.fields['tags'].queryset = TagsModel.objects.none()
                self.fields['listed_by'].queryset = ListedByModel.objects.none()
                self.fields['fuel'].queryset = FuelModel.objects.none()
                self.fields['transmission'].queryset = TransmissionModel.objects.none()
                self.fields['enquiry_type'].queryset = EnquiryTypeModel.objects.none()
        else:
            self.fields['type'].queryset = SubCategoryType.objects.none()
            self.fields['tags'].queryset = TagsModel.objects.none()
            self.fields['listed_by'].queryset = ListedByModel.objects.none()
            self.fields['fuel'].queryset = FuelModel.objects.none()
            self.fields['transmission'].queryset = TransmissionModel.objects.none()
            self.fields['enquiry_type'].queryset = EnquiryTypeModel.objects.none()

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if len(tags) == 0:
            raise forms.ValidationError("Please select atleast 1 tags")
        return tags


class GeneralAdForm(ModelForm):
    class Meta:
        model = GeneralSubCategory
        fields = "__all__"
        exclude = ("sub_category", "category", "user", "approved", "transaction", "start_date", "end_date", "expired",
                   "payment_status", "slug")

    def __init__(self, *args, **kwargs):
        sub_category = kwargs.pop('sub_category', None)
        super().__init__(*args, **kwargs)
        self.fields['enquiry_type'].required = True
        if sub_category:
            sub_category_type_queryset = SubCategoryType.objects.filter(sub_category=sub_category)
            self.fields['type'].queryset = sub_category_type_queryset

            self.fields['tags'].widget = forms.CheckboxSelectMultiple()
            if sub_category_type_queryset:
                category_queryset = TagsModel.objects.filter(
                    category=sub_category_type_queryset.first().sub_category.category)
                self.fields['tags'].queryset = category_queryset
                self.fields['enquiry_type'].queryset = EnquiryTypeModel.objects.filter(sub_category=sub_category)
            else:
                self.fields['tags'].queryset = TagsModel.objects.none()
                self.fields['enquiry_type'].queryset = EnquiryTypeModel.objects.none()
        else:
            self.fields['type'].queryset = SubCategoryType.objects.none()
            self.fields['tags'].queryset = TagsModel.objects.none()
            self.fields['enquiry_type'].queryset = EnquiryTypeModel.objects.none()

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if len(tags) == 0:
            raise forms.ValidationError("Please select atleast 1 tags")
        return tags


class JobsAdForm(ModelForm):
    class Meta:
        model = JobsSubCategory
        fields = "__all__"
        exclude = ("sub_category", "category", "user", "approved", "transaction", "start_date", "end_date", "expired",
                   "payment_status", "slug")

    def __init__(self, *args, **kwargs):
        sub_category = kwargs.pop('sub_category', None)
        super().__init__(*args, **kwargs)
        self.fields['enquiry_type'].required = True
        
        self.fields['tags'].widget = forms.CheckboxSelectMultiple()
        
        if sub_category:
            sub_category_type_queryset = SubCategoryType.objects.filter(sub_category=sub_category)
            self.fields['type'].queryset = sub_category_type_queryset

            if sub_category_type_queryset:
                category_queryset = TagsModel.objects.filter(
                    category=sub_category_type_queryset.first().sub_category.category)
                self.fields['tags'].queryset = category_queryset
                self.fields['enquiry_type'].queryset = EnquiryTypeModel.objects.filter(sub_category=sub_category)
            else:
                self.fields['tags'].queryset = TagsModel.objects.none()
                self.fields['enquiry_type'].queryset = EnquiryTypeModel.objects.none()
        else:
            self.fields['type'].queryset = SubCategoryType.objects.none()
            self.fields['tags'].queryset = TagsModel.objects.none()
            self.fields['enquiry_type'].queryset = EnquiryTypeModel.objects.none()

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if len(tags) == 0:
            raise forms.ValidationError("Please select atleast 1 tags")
        return tags


class CompanyAdForm(ModelForm):
    class Meta:
        model = CompanySubCategory
        fields = "__all__"
        exclude = ("sub_category", "category", "user", "approved","total_price", "transaction", "start_date",
                   "end_date", "expired", "payment_status", "slug")

    def __init__(self, *args, **kwargs):
        sub_category = kwargs.pop('sub_category', None)
        super().__init__(*args, **kwargs)
        
        self.fields['tags'].widget = forms.CheckboxSelectMultiple()
        if sub_category:
            sub_category_type_queryset = SubCategoryType.objects.filter(sub_category=sub_category)
            self.fields['type'].queryset = sub_category_type_queryset

            if sub_category_type_queryset:
                category_queryset = TagsModel.objects.filter(
                    category=sub_category_type_queryset.first().sub_category.category)
                self.fields['tags'].queryset = category_queryset
                self.fields['enquiry_type'].queryset = EnquiryTypeModel.objects.filter(sub_category=sub_category)
            else:
                self.fields['tags'].queryset = TagsModel.objects.none()
                self.fields['enquiry_type'].queryset = EnquiryTypeModel.objects.none()
        else:
            self.fields['type'].queryset = SubCategoryType.objects.none()
            self.fields['tags'].queryset = TagsModel.objects.none()
            self.fields['enquiry_type'].queryset = EnquiryTypeModel.objects.none()

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if len(tags) == 0:
            raise forms.ValidationError("Please select atleast 1 tags")
        return tags


class ArticleAdForm(ModelForm):
    class Meta:
        model = ArticleSubCategory
        fields = "__all__"
        exclude = ("sub_category", "category", "user", "total_price", "approved", "transaction", "start_date",
                   "end_date", "expired", "payment_status", "slug")

    def __init__(self, *args, **kwargs):
        sub_category = kwargs.pop('sub_category', None)
        super().__init__(*args, **kwargs)
        
        self.fields['tags'].widget = forms.CheckboxSelectMultiple()
        if sub_category:
            sub_category_type_queryset = SubCategoryType.objects.filter(sub_category=sub_category)
            self.fields['type'].queryset = sub_category_type_queryset

            if sub_category_type_queryset:
                category_queryset = TagsModel.objects.filter(
                    category=sub_category_type_queryset.first().sub_category.category)
                self.fields['tags'].queryset = category_queryset
                # self.fields['enquiry_type'].queryset = EnquiryTypeModel.objects.filter(sub_category=sub_category)
            else:
                self.fields['tags'].queryset = TagsModel.objects.none()
                # self.fields['enquiry_type'].queryset = EnquiryTypeModel.objects.none()
        else:
            self.fields['type'].queryset = SubCategoryType.objects.none()
            self.fields['tags'].queryset = TagsModel.objects.none()
            # self.fields['enquiry_type'].queryset = EnquiryTypeModel.objects.none()

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if len(tags) == 0:
            raise forms.ValidationError("Please select atleast 1 tags")
        return tags


class EnquiryForm(ModelForm):
    cv = forms.FileField(required=False)

    class Meta:
        model = EnquiryModel
        fields = ("name", "email", "message")

    def __init__(self, *args, **kwargs):
        ad_type = kwargs.pop('ad_type', None)
        super().__init__(*args, **kwargs)
        if ad_type == "Jobs":
            # If ad_type is "Jobs", make 'cv' required and keep it in the form
            self.fields['cv'].required = True
        else:
            # If ad_type is not "Jobs", remove 'cv' field from the form
            self.fields.pop('cv', None)


class ProfileUpdateForm(ModelForm):
    class Meta:
        model = UserModel
        fields = ("full_name", "email", "country_code", "mobile_number","profile_image")

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['class'] = 'read-only-field'



