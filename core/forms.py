from django import forms
from django.contrib.auth.models import User
from .models import WorkoutSession
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import (
    UserProfile, LifeSetup, DailyLog,
    MeaningfulActions, ReflectionJournal, HealthTracker
)


# ─────────────────────────────────────────
# 1. Registration Form
# ─────────────────────────────────────────
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })
        self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['email'].widget.attrs['placeholder'] = 'Email Address'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'


# ─────────────────────────────────────────
# 2. Login Form
# ─────────────────────────────────────────
class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username',
            'autocomplete': 'off'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })


# ─────────────────────────────────────────
# 3. User Profile Form
# ─────────────────────────────────────────
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tell us a little about yourself...'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }


# ─────────────────────────────────────────
# 4. Life Setup Form
# ─────────────────────────────────────────
PRIORITY_CHOICES = [
    ('career', 'Career'),
    ('health', 'Health'),
    ('learning', 'Learning'),
    ('family', 'Family'),
    ('financial_freedom', 'Financial Freedom'),
    ('discipline', 'Discipline'),
    ('relationships', 'Relationships'),
    ('peace_of_mind', 'Peace of Mind'),
    ('spiritual_growth', 'Spiritual Growth'),
]

class LifeSetupForm(forms.ModelForm):
    priorities = forms.MultipleChoiceField(
        choices=PRIORITY_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'priority-checkbox'
        }),
        required=True,
        help_text="Select what matters most to you in life."
    )

    class Meta:
        model = LifeSetup
        fields = ['current_age', 'expected_lifespan', 'priorities']
        widgets = {
            'current_age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your current age',
                'min': 1,
                'max': 120
            }),
            'expected_lifespan': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Expected lifespan (default: 80)',
                'min': 1,
                'max': 120
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        age = cleaned_data.get('current_age')
        lifespan = cleaned_data.get('expected_lifespan')
        if age and lifespan and age >= lifespan:
            raise forms.ValidationError(
                "Expected lifespan must be greater than your current age."
            )
        return cleaned_data


# ─────────────────────────────────────────
# 5. Daily Log Form (Quick Check)
# ─────────────────────────────────────────
class DailyLogForm(forms.ModelForm):
    class Meta:
        model = DailyLog
        fields = [
            'sleep_hours', 'wake_up_time',
            'study_hours', 'physical_activity_minutes',
            'screen_time_hours', 'water_intake_liters',
            'mood', 'energy_level'
        ]
        widgets = {
            'sleep_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 7.5',
                'min': 0, 'max': 24, 'step': 0.5
            }),
            'wake_up_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'study_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 2',
                'min': 0, 'max': 24, 'step': 0.5
            }),
            'physical_activity_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 30',
                'min': 0
            }),
            'screen_time_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 3',
                'min': 0, 'max': 24, 'step': 0.5
            }),
            'water_intake_liters': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 2.5',
                'min': 0, 'max': 20, 'step': 0.1
            }),
            'mood': forms.Select(attrs={'class': 'form-select'}),
            'energy_level': forms.Select(attrs={'class': 'form-select'}),
        }

# ─────────────────────────────────────────
# 6. Meaningful Actions Form
# ─────────────────────────────────────────
class MeaningfulActionsForm(forms.ModelForm):
    class Meta:
        model = MeaningfulActions
        fields = [
            'learned_something',
            'exercised',
            'helped_someone',
            'quality_time_with_loved_ones',
            'avoided_bad_habit',
            'worked_toward_future',
            'took_care_of_mental_health',
        ]
        widgets = {
            'learned_something': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'exercised': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'helped_someone': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'quality_time_with_loved_ones': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'avoided_bad_habit': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'worked_toward_future': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'took_care_of_mental_health': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'learned_something': 'I learned something new today',
            'exercised': 'I exercised today',
            'helped_someone': 'I helped someone today',
            'quality_time_with_loved_ones': 'I spent quality time with family or friends',
            'avoided_bad_habit': 'I avoided a bad habit today',
            'worked_toward_future': 'I worked toward my future goals',
            'took_care_of_mental_health': 'I took care of my mental health',
        }


# ─────────────────────────────────────────
# 7. Daily Reflection Journal Form
# ─────────────────────────────────────────
class ReflectionJournalForm(forms.ModelForm):
    class Meta:
        model = ReflectionJournal
        fields = ['entry']
        widgets = {
            'entry': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Write freely about your day...\n\nWhat did you learn? How did you feel? What went well? What could be better?'
            }),
        }
        labels = {
            'entry': 'Your Reflection'
        }
        
# ─────────────────────────────────────────
# 8. Health Tracker Form
# ─────────────────────────────────────────
class HealthTrackerForm(forms.ModelForm):
    class Meta:
        model = HealthTracker
        fields = ['activity_level', 'average_sleep_hours', 'workout_days_per_week']
        widgets = {
            'activity_level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'average_sleep_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Average sleep hours per night',
                'min': 0, 'max': 24, 'step': 0.5
            }),
            'workout_days_per_week': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Workout days per week',
                'min': 0, 'max': 7
            }),
        }
        labels = {
            'activity_level': 'Your Activity Level',
            'average_sleep_hours': 'Average Sleep Hours Per Night',
            'workout_days_per_week': 'Workout Days Per Week',
        }
class WorkoutSessionForm(forms.ModelForm):
    class Meta:
        model = WorkoutSession
        fields = ['workout_type', 'duration_minutes', 'intensity', 'notes']
        widgets = {
            'workout_type': forms.Select(attrs={'class': 'form-select'}),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 45',
                'min': 1
            }),
            'intensity': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional — what did you do specifically? e.g. bench press, 5km run...'
            }),
        }
        labels = {
            'workout_type': 'Workout Type',
            'duration_minutes': 'Duration (minutes)',
            'intensity': 'Intensity',
            'notes': 'Details (optional)',
        }