from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# ─────────────────────────────────────────
# 1. User Profile
# ─────────────────────────────────────────
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


# ─────────────────────────────────────────
# 2. Life Setup
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

class LifeSetup(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='life_setup')
    current_age = models.PositiveIntegerField()
    expected_lifespan = models.PositiveIntegerField(default=80)
    priorities = models.JSONField(default=list)  # stores list of selected priorities
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def years_remaining(self):
        return max(self.expected_lifespan - self.current_age, 0)

    @property
    def months_remaining(self):
        return self.years_remaining * 12

    @property
    def weeks_remaining(self):
        return self.years_remaining * 52

    @property
    def days_remaining(self):
        return self.years_remaining * 365

    @property
    def hours_remaining(self):
        return self.days_remaining * 24

    @property
    def life_used_percentage(self):
        return round((self.current_age / self.expected_lifespan) * 100, 2)

    @property
    def life_remaining_percentage(self):
        return round(100 - self.life_used_percentage, 2)

    def __str__(self):
        return f"{self.user.username}'s Life Setup"


# ─────────────────────────────────────────
# 3. Daily Log (Quick Check)
# ─────────────────────────────────────────
MOOD_CHOICES = [(i, str(i)) for i in range(1, 11)]
ENERGY_CHOICES = [(i, str(i)) for i in range(1, 11)]

class DailyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_logs')
    date = models.DateField()

    # Health & Habits
    sleep_hours = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(24)])
    wake_up_time = models.TimeField()
    study_hours = models.FloatField(default=0)
    physical_activity_minutes = models.PositiveIntegerField(default=0)
    screen_time_hours = models.FloatField(default=0)
    water_intake_liters = models.FloatField(default=0)

    # Mood & Energy
    mood = models.IntegerField(choices=MOOD_CHOICES)
    energy_level = models.IntegerField(choices=ENERGY_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - Daily Log {self.date}"


# ─────────────────────────────────────────
# 4. Meaningful Actions Tracker
# ─────────────────────────────────────────
class MeaningfulActions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meaningful_actions')
    date = models.DateField()

    learned_something = models.BooleanField(default=False)
    exercised = models.BooleanField(default=False)
    helped_someone = models.BooleanField(default=False)
    quality_time_with_loved_ones = models.BooleanField(default=False)
    avoided_bad_habit = models.BooleanField(default=False)
    worked_toward_future = models.BooleanField(default=False)
    took_care_of_mental_health = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    @property
    def total_actions_completed(self):
        fields = [
            self.learned_something,
            self.exercised,
            self.helped_someone,
            self.quality_time_with_loved_ones,
            self.avoided_bad_habit,
            self.worked_toward_future,
            self.took_care_of_mental_health,
        ]
        return sum(fields)

    def __str__(self):
        return f"{self.user.username} - Actions {self.date}"


# ─────────────────────────────────────────
# 5. Daily Reflection Journal
# ─────────────────────────────────────────
class ReflectionJournal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journals')
    date = models.DateField()
    entry = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - Journal {self.date}"


# ─────────────────────────────────────────
# 6. AI Insights
# ─────────────────────────────────────────
INSIGHT_TYPE_CHOICES = [
    ('daily', 'Daily Reflection'),
    ('weekly', 'Weekly Analysis'),
    ('monthly', 'Monthly Summary'),
    ('motivational', 'Motivational Quote'),
    ('health', 'Health Suggestion'),
    ('pattern', 'Behavior Pattern'),
]

class AIInsight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_insights')
    date = models.DateField()
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPE_CHOICES)
    content = models.TextField()
    motivational_quote = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - AI Insight ({self.insight_type}) {self.date}"


# ─────────────────────────────────────────
# 7. Weekly Report
# ─────────────────────────────────────────
class WeeklyReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weekly_reports')
    week_start = models.DateField()
    week_end = models.DateField()

    # Life Scores (0–10)
    learning_score = models.FloatField(default=0)
    health_score = models.FloatField(default=0)
    discipline_score = models.FloatField(default=0)
    relationships_score = models.FloatField(default=0)
    consistency_score = models.FloatField(default=0)

    ai_summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def overall_score(self):
        scores = [
            self.learning_score,
            self.health_score,
            self.discipline_score,
            self.relationships_score,
            self.consistency_score,
        ]
        return round(sum(scores) / len(scores), 2)

    class Meta:
        ordering = ['-week_start']

    def __str__(self):
        return f"{self.user.username} - Week {self.week_start} to {self.week_end}"


# ─────────────────────────────────────────
# 8. Monthly Report
# ─────────────────────────────────────────
class MonthlyReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='monthly_reports')
    month = models.PositiveIntegerField()  # 1–12
    year = models.PositiveIntegerField()
    total_meaningful_hours = models.FloatField(default=0)
    ai_summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'month', 'year')
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.user.username} - {self.month}/{self.year} Report"


# ─────────────────────────────────────────
# 9. Streak Tracker
# ─────────────────────────────────────────
class StreakTracker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streaks')

    study_streak = models.PositiveIntegerField(default=0)
    study_streak_best = models.PositiveIntegerField(default=0)
    last_study_date = models.DateField(blank=True, null=True)

    workout_streak = models.PositiveIntegerField(default=0)
    workout_streak_best = models.PositiveIntegerField(default=0)
    last_workout_date = models.DateField(blank=True, null=True)

    no_procrastination_streak = models.PositiveIntegerField(default=0)
    no_procrastination_best = models.PositiveIntegerField(default=0)
    last_no_procrastination_date = models.DateField(blank=True, null=True)

    good_deed_streak = models.PositiveIntegerField(default=0)
    good_deed_streak_best = models.PositiveIntegerField(default=0)
    last_good_deed_date = models.DateField(blank=True, null=True)

    discipline_streak = models.PositiveIntegerField(default=0)
    discipline_streak_best = models.PositiveIntegerField(default=0)
    last_discipline_date = models.DateField(blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Streaks"


# ─────────────────────────────────────────
# 10. Health Tracker
# ─────────────────────────────────────────
ACTIVITY_LEVEL_CHOICES = [
    ('sedentary', 'Sedentary'),
    ('light', 'Light Activity'),
    ('moderate', 'Moderate Activity'),
    ('active', 'Very Active'),
]

class HealthTracker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='health')
    activity_level = models.CharField(
        max_length=20,
        choices=ACTIVITY_LEVEL_CHOICES,
        default='moderate'
    )
    average_sleep_hours = models.FloatField(default=7)
    workout_days_per_week = models.PositiveIntegerField(default=3)
    ai_health_suggestion = models.TextField(blank=True, null=True)
    last_suggestion_date = models.DateField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Health Tracker"


# ─────────────────────────────────────────
# 11. Motivation Messages
# ─────────────────────────────────────────
TRIGGER_CHOICES = [
    ('studied_well', 'Studied Well'),
    ('completed_workout', 'Completed Workout'),
    ('avoided_procrastination', 'Avoided Procrastination'),
    ('difficult_day', 'Difficult Day'),
    ('general', 'General'),
    ('helped_someone', 'Helped Someone'),
    ('quality_time', 'Quality Time with Loved Ones'),
    ('mental_health', 'Took Care of Mental Health'),
]
# ─────────────────────────────────────────
# 12. Workout Session
# ─────────────────────────────────────────
WORKOUT_TYPE_CHOICES = [
    ('strength', 'Strength Training'),
    ('cardio', 'Cardio'),
    ('yoga', 'Yoga'),
    ('stretching', 'Stretching'),
    ('sports', 'Sports'),
    ('walking', 'Walking'),
    ('cycling', 'Cycling'),
    ('swimming', 'Swimming'),
    ('hiit', 'HIIT'),
    ('other', 'Other'),
]

INTENSITY_CHOICES = [
    ('light', 'Light'),
    ('moderate', 'Moderate'),
    ('intense', 'Intense'),
]

class WorkoutSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts')
    date = models.DateField()
    workout_type = models.CharField(max_length=20, choices=WORKOUT_TYPE_CHOICES)
    duration_minutes = models.PositiveIntegerField()
    intensity = models.CharField(max_length=10, choices=INTENSITY_CHOICES)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.workout_type} on {self.date}"

class MotivationMessage(models.Model):
    trigger = models.CharField(max_length=30, choices=TRIGGER_CHOICES)
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Motivation - {self.trigger}"