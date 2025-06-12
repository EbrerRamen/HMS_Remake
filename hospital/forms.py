from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import UserProfile, Department, Shift, Admission, Ward, Bed, PatientProfile, Billing, DoctorProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['username', 'first_name', 'last_name', 'email', 'gender', 'address', 'date_of_birth', 'contact_no', 'account_type']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'contact_no': forms.NumberInput(attrs={'pattern': '[0-9]{10}', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'account_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make certain fields required
        self.fields['username'].required = True
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['gender'].required = True
        self.fields['address'].required = True
        self.fields['date_of_birth'].required = True
        self.fields['contact_no'].required = True
        self.fields['account_type'].required = True

        # Add help text
        self.fields['contact_no'].help_text = 'Enter a 10-digit number starting with 15-19'
        self.fields['date_of_birth'].help_text = 'Select date of birth'

class AdminProfileForm(UserChangeForm):
    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES)
    address = forms.CharField(max_length=200)
    date_of_birth = forms.DateField()
    contact_no = forms.IntegerField(
        validators=[
            MinValueValidator(1500000000),  
            MaxValueValidator(1999999999)
        ]
    ) 

    class Meta:
        model = UserProfile
        fields = ['username', 'first_name', 'last_name', 'email', 'gender', 'address', 'date_of_birth', 'contact_no']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['account_type'] = 'admin'
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.account_type = 'admin'
        if commit:
            instance.save()
        return instance

class UserFilterForm(forms.Form):
    GENDER_CHOICES = [('', '---------')] + UserProfile.GENDER_CHOICES
    ACCOUNT_TYPE_CHOICES = [('', '---------')] + UserProfile.ACCOUNT_TYPE_CHOICES

    search_query = forms.CharField(label='Search by Username', required=False)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False, initial='')
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE_CHOICES, required=False, initial='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gender'].initial = ''  
        self.fields['account_type'].initial = ''

class PatientFilterForm(forms.Form):
    search_query = forms.CharField(label='Search by Username', required=False)

class DoctorFilterForm(forms.Form):
    search_query = forms.CharField(label='Search by Username',required=False)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False, empty_label='Select department')

class DoctorUserFilterForm(forms.Form):
    search_query = forms.CharField(label='Search by Name',required=False)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False, empty_label='Select department')

class WardFilterForm(forms.Form):
    WARD_CHOICES = [('', '---------')] + list(Ward.WARD_TYPES)

    ward_type = forms.ChoiceField(choices=WARD_CHOICES, required=False, label='Ward Type', initial='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ward_type'].initial = ''  


class BedFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ward_choices = [('', '---------')] + [(ward.id, ward) for ward in Ward.objects.all()]
        self.fields['ward'] = forms.ChoiceField(choices=ward_choices, required=False, label='Ward')

    bed_number = forms.IntegerField(required=False, label='Bed Number')

class BillingFilterForm(forms.Form):
    search_query = forms.IntegerField(label='Search by Billing ID',required=False )
    date = forms.DateField(required=False, label='Date')
    STATUS_CHOICES = [('', '---------')] + Billing.STATUS_CHOICES
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, label='Status')
    PAYMENT_METHOD_CHOICES = [('', '---------')] + Billing.PAYMENT_METHOD_CHOICES
    payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES, required=False, label='Payment Method')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        self.fields['status'].initial = ''

class AdmissionFilterForm(forms.Form):
    search_query = forms.CharField(label='Search by Username or Name', required=False)
    WARD_TYPES = [('', '---------')] + Ward.WARD_TYPES
    ward_type = forms.ChoiceField(choices=WARD_TYPES, required=False, label='Ward Type')
    sort_by = forms.ChoiceField(
        label='Sort by',
        choices=(
            ('', 'Select'),
            ('admission_datetime', 'Admission Date'),
        ),
        required=False
    )

class DoctorRequestFilterForm(forms.Form):
    search_query = forms.CharField(label='Search by Username', required=False)

class DeptShifts(forms.Form):
    department = forms.ModelChoiceField(queryset=Department.objects.all())
    shift = forms.ModelChoiceField(queryset=Shift.objects.all())

class AdmissionForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = ['patient', 'bed', 'admission_datetime'] 
        widgets = {
            'admission_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'head_doctor']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['head_doctor'].queryset = DoctorProfile.objects.filter(
            user_profile__is_approved=True,
            user_profile__account_type='doctor'
        )

class WardForm(forms.ModelForm):
    class Meta:
        model = Ward
        fields = ['name', 'ward_type']

class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ['type', 'start_time', 'end_time']

class BedForm(forms.ModelForm):
    class Meta:
        model = Bed
        fields = ['ward', 'bed_number'] 
        
class BillingForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = ['patient', 'total_amount', 'date', 'status', 'payment_method']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter patients to show only those with active admissions
        admitted_patients = PatientProfile.objects.filter(admission__isnull=False)
        self.fields['patient'].queryset = admitted_patients
        self.fields['patient'].label_from_instance = lambda obj: f"{obj.user_profile.get_full_name()} (Admitted)"

class DoctorForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES, required=True)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    contact_no = forms.IntegerField(
        validators=[MinValueValidator(1500000000), MaxValueValidator(1999999999)],
        required=True
    )
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=True)
    specialization = forms.CharField(max_length=100, required=True)
    qualifications = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True)
    shift = forms.ModelChoiceField(queryset=Shift.objects.all(), required=True)

    class Meta:
        model = DoctorProfile
        fields = ['username', 'email', 'first_name', 'last_name', 'gender', 'address', 
                 'date_of_birth', 'contact_no', 'password', 'confirm_password',
                 'specialization', 'qualifications', 'department', 'shift']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['password', 'confirm_password']:
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs.update({'class': 'form-select'})
                else:
                    field.widget.attrs.update({'class': 'form-control'})

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return confirm_password

    def clean_contact_no(self):
        contact_no = self.cleaned_data.get('contact_no')
        if UserProfile.objects.filter(contact_no=contact_no).exists():
            raise forms.ValidationError("This contact number is already registered")
        return contact_no

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UserProfile.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if UserProfile.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken")
        return username

class PatientForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES, required=True, widget=forms.Select(attrs={'class': 'form-select'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), required=True)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=True)
    contact_no = forms.IntegerField(
        validators=[MinValueValidator(1500000000), MaxValueValidator(1999999999)],
        required=True,
        widget=forms.NumberInput(attrs={'pattern': '[0-9]{10}', 'class': 'form-control'})
    )

    class Meta:
        model = PatientProfile
        fields = ['username', 'first_name', 'last_name', 'email', 'gender', 'address', 
                 'date_of_birth', 'contact_no', 'medical_history', 'prescribed_medications']
        widgets = {
            'medical_history': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'prescribed_medications': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user_profile = kwargs.pop('user_profile', None)
        super().__init__(*args, **kwargs)

        if user_profile:
            self.fields['username'].initial = user_profile.username
            self.fields['first_name'].initial = user_profile.first_name
            self.fields['last_name'].initial = user_profile.last_name
            self.fields['email'].initial = user_profile.email
            self.fields['gender'].initial = user_profile.gender
            self.fields['address'].initial = user_profile.address
            self.fields['date_of_birth'].initial = user_profile.date_of_birth
            self.fields['contact_no'].initial = user_profile.contact_no
        
        # Add 'form-control' class to all fields
        for field_name, field in self.fields.items():
            if field_name not in ['username', 'first_name', 'last_name', 'email', 'gender', 'address', 'date_of_birth', 'contact_no']:
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs.update({'class': 'form-select'})
                else:
                    field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        patient_profile = super().save(commit=False)
        user_profile = patient_profile.user_profile

        user_profile.username = self.cleaned_data['username']
        user_profile.first_name = self.cleaned_data['first_name']
        user_profile.last_name = self.cleaned_data['last_name']
        user_profile.email = self.cleaned_data['email']
        user_profile.gender = self.cleaned_data['gender']
        user_profile.address = self.cleaned_data['address']
        user_profile.date_of_birth = self.cleaned_data['date_of_birth']
        user_profile.contact_no = self.cleaned_data['contact_no']

        if commit:
            user_profile.save()
            patient_profile.save()
        return patient_profile


class PatientProfileUpdateForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES, required=True)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    contact_no = forms.IntegerField(
        validators=[MinValueValidator(1500000000), MaxValueValidator(1999999999)],
        required=True
    )

    class Meta:
        model = PatientProfile
        fields = [
            'medical_history', 'prescribed_medications',
            'username', 'first_name', 'last_name', 'email', 'gender', 
            'address', 'date_of_birth', 'contact_no'
        ]
        widgets = {
            'medical_history': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'prescribed_medications': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'contact_no': forms.NumberInput(attrs={'pattern': '[0-9]{10}', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user_profile = kwargs.pop('user_profile', None)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.user_profile:
            self.fields['username'].initial = self.instance.user_profile.username
            self.fields['first_name'].initial = self.instance.user_profile.first_name
            self.fields['last_name'].initial = self.instance.user_profile.last_name
            self.fields['email'].initial = self.instance.user_profile.email
            self.fields['gender'].initial = self.instance.user_profile.gender
            self.fields['address'].initial = self.instance.user_profile.address
            self.fields['date_of_birth'].initial = self.instance.user_profile.date_of_birth
            self.fields['contact_no'].initial = self.instance.user_profile.contact_no

    def save(self, commit=True):
        patient_profile = super().save(commit=False)
        user_profile = patient_profile.user_profile

        user_profile.username = self.cleaned_data['username']
        user_profile.first_name = self.cleaned_data['first_name']
        user_profile.last_name = self.cleaned_data['last_name']
        user_profile.email = self.cleaned_data['email']
        user_profile.gender = self.cleaned_data['gender']
        user_profile.address = self.cleaned_data['address']
        user_profile.date_of_birth = self.cleaned_data['date_of_birth']
        user_profile.contact_no = self.cleaned_data['contact_no']

        if commit:
            user_profile.save()
            patient_profile.save()
        return patient_profile

