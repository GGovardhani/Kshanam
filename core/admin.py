from django.contrib import admin
from .models import WorkoutSession

from .models import (
    UserProfile, LifeSetup, DailyLog, MeaningfulActions,
    ReflectionJournal, AIInsight, WeeklyReport, MonthlyReport,
    StreakTracker, HealthTracker, MotivationMessage
)

admin.site.register(UserProfile)
admin.site.register(LifeSetup)
admin.site.register(DailyLog)
admin.site.register(MeaningfulActions)
admin.site.register(ReflectionJournal)
admin.site.register(AIInsight)
admin.site.register(WeeklyReport)
admin.site.register(MonthlyReport)
admin.site.register(StreakTracker)
admin.site.register(HealthTracker)
admin.site.register(WorkoutSession)
admin.site.register(MotivationMessage)