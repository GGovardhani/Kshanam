from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Sum
from .ai_helper import (
    get_daily_reflection, get_motivational_quote,
    get_weekly_scores, get_monthly_summary,
    get_health_suggestion, get_future_self_message
)
from .forms import (
    RegisterForm, LoginForm, UserProfileForm,
    LifeSetupForm, DailyLogForm, MeaningfulActionsForm,
    ReflectionJournalForm, HealthTrackerForm, WorkoutSessionForm
)
from .models import (
    UserProfile, LifeSetup, DailyLog,
    MeaningfulActions, ReflectionJournal, AIInsight,
    WeeklyReport, MonthlyReport, StreakTracker,
    HealthTracker, WorkoutSession
)
import datetime
import json

from .forms import (
    RegisterForm, LoginForm, UserProfileForm,
    LifeSetupForm, DailyLogForm, MeaningfulActionsForm,
    ReflectionJournalForm, HealthTrackerForm
)
from .models import (
    UserProfile, LifeSetup, DailyLog,
    MeaningfulActions, ReflectionJournal, AIInsight,
    WeeklyReport, MonthlyReport, StreakTracker, HealthTracker
)
from .ai_helper import (
    get_daily_reflection, get_motivational_quote,
    get_weekly_scores, get_monthly_summary, get_health_suggestion
)


# ─────────────────────────────────────────
# Helper: get or create related objects
# ─────────────────────────────────────────
def get_or_create_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile

def get_or_create_streaks(user):
    streaks, _ = StreakTracker.objects.get_or_create(user=user)
    return streaks

def get_or_create_health(user):
    health, _ = HealthTracker.objects.get_or_create(user=user)
    return health


# ─────────────────────────────────────────
# Update streaks based on today's actions
# ─────────────────────────────────────────
def update_streaks(user, daily_log, meaningful_actions):
    streaks = get_or_create_streaks(user)
    today = timezone.now().date()

    def update(current, best, last_date, condition):
        if condition:
            if last_date == today - datetime.timedelta(days=1) or last_date == today:
                current += 1 if last_date != today else 0
            else:
                current = 1
            best = max(best, current)
            last_date = today
        return current, best, last_date

    streaks.study_streak, streaks.study_streak_best, streaks.last_study_date = update(
        streaks.study_streak, streaks.study_streak_best,
        streaks.last_study_date, daily_log.study_hours >= 1
    )
    streaks.workout_streak, streaks.workout_streak_best, streaks.last_workout_date = update(
        streaks.workout_streak, streaks.workout_streak_best,
        streaks.last_workout_date, meaningful_actions.exercised
    )
    streaks.no_procrastination_streak, streaks.no_procrastination_best, streaks.last_no_procrastination_date = update(
        streaks.no_procrastination_streak, streaks.no_procrastination_best,
        streaks.last_no_procrastination_date, meaningful_actions.avoided_bad_habit
    )
    streaks.good_deed_streak, streaks.good_deed_streak_best, streaks.last_good_deed_date = update(
        streaks.good_deed_streak, streaks.good_deed_streak_best,
        streaks.last_good_deed_date, meaningful_actions.helped_someone
    )
    streaks.discipline_streak, streaks.discipline_streak_best, streaks.last_discipline_date = update(
        streaks.discipline_streak, streaks.discipline_streak_best,
        streaks.last_discipline_date,
        daily_log.study_hours >= 1 and meaningful_actions.exercised
    )
    streaks.save()


# ─────────────────────────────────────────
# Landing Page
# ─────────────────────────────────────────
def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/landing.html')


# ─────────────────────────────────────────
# Register
# ─────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            get_or_create_profile(user)
            get_or_create_streaks(user)
            get_or_create_health(user)
            login(request, user)
            messages.success(request, f"Welcome to Kshanam, {user.first_name}! Let's set up your life profile.")
            return redirect('life_setup')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})


# ─────────────────────────────────────────
# Login
# ─────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})


# ─────────────────────────────────────────
# Logout
# ─────────────────────────────────────────
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out. See you tomorrow.")
    return redirect('landing')


# ─────────────────────────────────────────
# Life Setup
# ─────────────────────────────────────────
@login_required
def life_setup_view(request):
    instance = LifeSetup.objects.filter(user=request.user).first()
    if request.method == 'POST':
        form = LifeSetupForm(request.POST, instance=instance)
        if form.is_valid():
            life_setup = form.save(commit=False)
            life_setup.user = request.user
            life_setup.priorities = form.cleaned_data['priorities']
            life_setup.save()
            messages.success(request, "Life setup saved. Your journey begins now.")
            return redirect('dashboard')
    else:
        initial = {}
        if instance:
            initial['priorities'] = instance.priorities
        form = LifeSetupForm(instance=instance, initial=initial)
    return render(request, 'core/life_setup.html', {'form': form})


# ─────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────
@login_required
def dashboard(request):
    life_setup = LifeSetup.objects.filter(user=request.user).first()
    if not life_setup:
        messages.warning(request, "Please complete your life setup first.")
        return redirect('life_setup')

    streaks = get_or_create_streaks(request.user)
    today = timezone.now().date()
    today_log = DailyLog.objects.filter(user=request.user, date=today).first()
    today_actions = MeaningfulActions.objects.filter(user=request.user, date=today).first()
    today_journal = ReflectionJournal.objects.filter(user=request.user, date=today).first()
    latest_insight = AIInsight.objects.filter(user=request.user).order_by('-created_at').first()

    # last 7 days mood data for chart
    last_7 = DailyLog.objects.filter(
        user=request.user,
        date__gte=today - datetime.timedelta(days=6)
    ).order_by('date')
    mood_data = [{'date': str(l.date), 'mood': l.mood, 'energy': l.energy_level} for l in last_7]

    # future self message — generate once per week
    future_message = None
    latest_weekly = WeeklyReport.objects.filter(user=request.user).order_by('-week_start').first()
    existing_future = AIInsight.objects.filter(
        user=request.user,
        insight_type='motivational',
        date=today
    ).first()

    if not existing_future and today_log:
        try:
            future_msg = get_future_self_message(life_setup, latest_weekly)
            existing_future = AIInsight.objects.create(
                user=request.user,
                date=today,
                insight_type='motivational',
                content=future_msg,
            )
        except Exception:
            pass

    context = {
        'life_setup': life_setup,
        'streaks': streaks,
        'today': today,
        'today_log': today_log,
        'today_actions': today_actions,
        'today_journal': today_journal,
        'latest_insight': latest_insight,
        'future_insight': existing_future,
        'mood_data': json.dumps(mood_data),
    }
    return render(request, 'core/dashboard.html', context)


# ─────────────────────────────────────────
# Daily Entry (Log + Actions + Journal together)
# ─────────────────────────────────────────
@login_required
def daily_entry(request):
    today = timezone.now().date()
    log_instance = DailyLog.objects.filter(user=request.user, date=today).first()
    actions_instance = MeaningfulActions.objects.filter(user=request.user, date=today).first()
    journal_instance = ReflectionJournal.objects.filter(user=request.user, date=today).first()

    already_submitted = bool(log_instance and actions_instance and journal_instance)

    if request.method == 'POST':
        log_form = DailyLogForm(request.POST, instance=log_instance, prefix='log')
        actions_form = MeaningfulActionsForm(request.POST, instance=actions_instance, prefix='actions')
        journal_form = ReflectionJournalForm(request.POST, instance=journal_instance, prefix='journal')

        if log_form.is_valid() and actions_form.is_valid() and journal_form.is_valid():
            daily_log = log_form.save(commit=False)
            daily_log.user = request.user
            daily_log.date = today
            daily_log.save()

            actions = actions_form.save(commit=False)
            actions.user = request.user
            actions.date = today
            actions.save()

            journal = journal_form.save(commit=False)
            journal.user = request.user
            journal.date = today
            journal.save()

            update_streaks(request.user, daily_log, actions)

            life_setup = LifeSetup.objects.filter(user=request.user).first()
            priorities = life_setup.priorities if life_setup else []

            try:
                reflection = get_daily_reflection(journal.entry, daily_log, actions, priorities, request.user.first_name or request.user.username)
                quote = get_motivational_quote(actions, daily_log, priorities)
                AIInsight.objects.update_or_create(
                    user=request.user,
                    date=today,
                    insight_type='daily',
                    defaults={
                        'content': reflection,
                        'motivational_quote': quote
                    }
                )
            except Exception as e:
                print(f"AI ERROR: {e}")
                AIInsight.objects.update_or_create(
                    user=request.user,
                    date=today,
                    insight_type='daily',
                    defaults={
                        'content': 'Keep going. Every day you show up is a step forward.',
                        'motivational_quote': 'Your future is still being written.'
                    }
                )

            return redirect('daily_result')

        else:
            print("LOG FORM ERRORS:", log_form.errors)
            print("ACTIONS FORM ERRORS:", actions_form.errors)
            print("JOURNAL FORM ERRORS:", journal_form.errors)

    else:
        log_form = DailyLogForm(instance=log_instance, prefix='log')
        actions_form = MeaningfulActionsForm(instance=actions_instance, prefix='actions')
        journal_form = ReflectionJournalForm(instance=journal_instance, prefix='journal')

    context = {
        'log_form': log_form,
        'actions_form': actions_form,
        'journal_form': journal_form,
        'today': today,
        'already_submitted': already_submitted,
    }
    return render(request, 'core/daily_entry.html', context)

# ─────────────────────────────────────────
# Daily Result (AI Reflection Page)
# ─────────────────────────────────────────
@login_required
def daily_result(request):
    today = timezone.now().date()
    insight = AIInsight.objects.filter(
        user=request.user, date=today, insight_type='daily'
    ).order_by('-created_at').first()
    return render(request, 'core/daily_result.html', {'insight': insight, 'today': today})


# ─────────────────────────────────────────
# Weekly Report
# ─────────────────────────────────────────
@login_required
def weekly_report(request):
    today = timezone.now().date()
    week_start = today - datetime.timedelta(days=today.weekday())
    week_end = week_start + datetime.timedelta(days=6)

    existing = WeeklyReport.objects.filter(
        user=request.user, week_start=week_start
    ).first()

    if not existing:
        logs = DailyLog.objects.filter(user=request.user, date__range=(week_start, today))
        actions_list = MeaningfulActions.objects.filter(user=request.user, date__range=(week_start, today))
        journals = ReflectionJournal.objects.filter(user=request.user, date__range=(week_start, today))

        if logs.exists():
            try:
                scores = get_weekly_scores(list(logs), list(actions_list), list(journals))
                existing = WeeklyReport.objects.create(
                    user=request.user,
                    week_start=week_start,
                    week_end=week_end,
                    learning_score=scores.get('learning_score', 0),
                    health_score=scores.get('health_score', 0),
                    discipline_score=scores.get('discipline_score', 0),
                    relationships_score=scores.get('relationships_score', 0),
                    consistency_score=scores.get('consistency_score', 0),
                    ai_summary=scores.get('summary', '')
                )
            except Exception:
                pass

    context = {
        'report': existing,
        'week_start': week_start,
        'week_end': week_end,
    }
    return render(request, 'core/weekly_report.html', context)


# ─────────────────────────────────────────
# Monthly Report
# ─────────────────────────────────────────
@login_required
def monthly_report(request):
    today = timezone.now().date()
    month = today.month
    year = today.year

    existing = MonthlyReport.objects.filter(
        user=request.user, month=month, year=year
    ).first()

    if not existing:
        logs = DailyLog.objects.filter(
            user=request.user,
            date__month=month, date__year=year
        )
        if logs.exists():
            total_hours = sum(
                (l.study_hours + (l.physical_activity_minutes / 60)) for l in logs
            )
            life_setup = LifeSetup.objects.filter(user=request.user).first()
            priorities = life_setup.priorities if life_setup else []
            try:
                summary = get_monthly_summary(list(logs), total_hours, priorities)
                existing = MonthlyReport.objects.create(
                    user=request.user,
                    month=month,
                    year=year,
                    total_meaningful_hours=total_hours,
                    ai_summary=summary
                )
            except Exception:
                pass

    context = {
        'report': existing,
        'month': today.strftime('%B'),
        'year': year,
    }
    return render(request, 'core/monthly_report.html', context)


# ─────────────────────────────────────────
# Health Page
# ─────────────────────────────────────────
@login_required
def health_view(request):
    health = get_or_create_health(request.user)
    life_setup = LifeSetup.objects.filter(user=request.user).first()
    today = timezone.now().date()

    # last 5 workouts
    recent_workouts = WorkoutSession.objects.filter(user=request.user).order_by('-date')[:5]
    today_workout = WorkoutSession.objects.filter(user=request.user, date=today).first()

    if request.method == 'POST':
        # check which form was submitted
        if 'save_health' in request.POST:
            form = HealthTrackerForm(request.POST, instance=health)
            workout_form = WorkoutSessionForm()
            if form.is_valid():
                health = form.save()
                age = life_setup.current_age if life_setup else 25

                # get recent workouts for better AI context
                recent = list(WorkoutSession.objects.filter(
                    user=request.user
                ).order_by('-date')[:7])

                try:
                    suggestion = get_health_suggestion(
                        age,
                        health.activity_level,
                        health.average_sleep_hours,
                        health.workout_days_per_week,
                        recent
                    )
                    health.ai_health_suggestion = suggestion
                    health.last_suggestion_date = today
                    health.save()
                    messages.success(request, "Health profile updated.")
                except Exception as e:
                    print(f"HEALTH AI ERROR: {e}")
                    messages.warning(request, f"Health saved but AI suggestion unavailable: {e}")
                return redirect('health')

        elif 'log_workout' in request.POST:
            workout_form = WorkoutSessionForm(request.POST, instance=today_workout)
            form = HealthTrackerForm(instance=health)
            if workout_form.is_valid():
                workout = workout_form.save(commit=False)
                workout.user = request.user
                workout.date = today
                workout.save()
                messages.success(request, "Workout logged successfully.")
                return redirect('health')

    else:
        form = HealthTrackerForm(instance=health)
        workout_form = WorkoutSessionForm(instance=today_workout)

    context = {
        'form': form,
        'workout_form': workout_form,
        'health': health,
        'recent_workouts': recent_workouts,
        'today_workout': today_workout,
    }
    return render(request, 'core/health.html', context)


# ─────────────────────────────────────────
# Profile
# ─────────────────────────────────────────
@login_required
def profile_view(request):
    profile = get_or_create_profile(request.user)
    life_setup = LifeSetup.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    total_logs = DailyLog.objects.filter(user=request.user).count()
    total_journals = ReflectionJournal.objects.filter(user=request.user).count()
    streaks = get_or_create_streaks(request.user)

    context = {
        'form': form,
        'profile': profile,
        'life_setup': life_setup,
        'total_logs': total_logs,
        'total_journals': total_journals,
        'streaks': streaks,
    }
    return render(request, 'core/profile.html', context)


# ─────────────────────────────────────────
# Journal History
# ─────────────────────────────────────────
@login_required
def journal_history(request):
    journals = ReflectionJournal.objects.filter(
        user=request.user
    ).order_by('-date')[:30]
    return render(request, 'core/journal_history.html', {'journals': journals})


# ─────────────────────────────────────────
# Insights History
# ─────────────────────────────────────────
@login_required
def insights_history(request):
    insights = AIInsight.objects.filter(
        user=request.user
    ).order_by('-created_at')[:20]
    return render(request, 'core/insights_history.html', {'insights': insights})