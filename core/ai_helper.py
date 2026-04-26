import json
from groq import Groq
from django.conf import settings

MODEL = "llama-3.3-70b-versatile"


def get_client():
    return Groq(api_key=settings.GROQ_API_KEY)


def get_fallback_reflection(username, daily_log, meaningful_actions):
    name = username or "friend"
    good = []
    improve = []

    if daily_log.study_hours >= 2:
        good.append(f"you studied for {daily_log.study_hours} hours")
    if daily_log.sleep_hours >= 7:
        good.append(f"you got {daily_log.sleep_hours} hours of sleep")
    if meaningful_actions.exercised:
        good.append("you worked out today")
    if meaningful_actions.helped_someone:
        good.append("you helped someone today")
    if daily_log.water_intake_liters >= 2:
        good.append(f"you drank {daily_log.water_intake_liters}L of water")

    if daily_log.sleep_hours < 6:
        improve.append("try to get more sleep tonight")
    if daily_log.study_hours < 1:
        improve.append("try to put in at least 1 hour of study tomorrow")
    if daily_log.water_intake_liters < 2:
        improve.append("drink more water tomorrow")
    if daily_log.screen_time_hours > 5:
        improve.append("try to cut down screen time a bit tomorrow")

    good_text = " and ".join(good) if good else "you showed up today"
    improve_text = improve[0] if improve else "keep up the consistency"

    return f"{name}, {good_text} — that's solid progress. {improve_text.capitalize()}. Every day you log is a day you're paying attention to your life, and that already puts you ahead."


def get_fallback_quote(username, daily_log, meaningful_actions):
    name = username or "friend"

    if daily_log.study_hours >= 2:
        return f"You put in {daily_log.study_hours} hours of study today {name} — that's how futures are built."
    elif meaningful_actions.exercised:
        return f"Working out is never easy {name}, but you did it anyway. That's the whole game."
    elif meaningful_actions.avoided_bad_habit:
        return f"Avoiding that bad habit today {name} is a bigger win than it feels right now."
    elif daily_log.mood <= 4:
        return f"Tough day {name}, but you still showed up and logged it. That counts for a lot."
    elif meaningful_actions.helped_someone:
        return f"You helped someone today {name} — don't underestimate how much that matters."
    else:
        return f"Showing up consistently is the whole secret {name}. You're doing it."


def get_daily_reflection(journal_entry, daily_log, meaningful_actions, priorities, username="friend"):
    client = get_client()
    priorities_text = ', '.join(priorities) if priorities else 'general life improvement'
    name = username or "friend"

    prompt = f"""
You are Kshanam, a friendly and honest personal mentor.
The user's name is {name}. Use their name naturally once in the reflection.

Their priorities: {priorities_text}

Today's journal: "{journal_entry}"

Today's data:
- Sleep: {daily_log.sleep_hours} hours
- Study: {daily_log.study_hours} hours
- Exercise: {daily_log.physical_activity_minutes} minutes
- Screen time: {daily_log.screen_time_hours} hours
- Water: {daily_log.water_intake_liters} liters
- Mood: {daily_log.mood}/10
- Energy: {daily_log.energy_level}/10

What they did today:
- Learned something: {meaningful_actions.learned_something}
- Exercised: {meaningful_actions.exercised}
- Helped someone: {meaningful_actions.helped_someone}
- Quality time with loved ones: {meaningful_actions.quality_time_with_loved_ones}
- Avoided bad habit: {meaningful_actions.avoided_bad_habit}
- Worked toward future: {meaningful_actions.worked_toward_future}
- Took care of mental health: {meaningful_actions.took_care_of_mental_health}

Write a short reflection like a real friend talking to {name} — casual, warm, direct.
3 to 4 sentences. Simple everyday words.
Use their name once naturally.
Point out something specific they did well today.
Mention one thing they could improve tomorrow — gentle not harsh.
No poetry. No metaphors. Just talk like a real person.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are Kshanam, a friendly personal mentor. Talk like a real person — simple, warm, direct. No poetry. No fancy words."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=250,
        temperature=0.75,
    )

    return response.choices[0].message.content.strip()


def get_motivational_quote(meaningful_actions, daily_log, priorities, username="friend"):
    client = get_client()
    priorities_text = ', '.join(priorities) if priorities else 'life improvement'
    name = username or "friend"

    if daily_log.study_hours >= 2:
        trigger = f"studied for {daily_log.study_hours} hours today"
    elif meaningful_actions.exercised:
        trigger = "worked out today"
    elif meaningful_actions.avoided_bad_habit:
        trigger = "avoided a bad habit today"
    elif daily_log.mood <= 4:
        trigger = "had a tough day today"
    elif meaningful_actions.helped_someone:
        trigger = "helped someone today"
    elif meaningful_actions.quality_time_with_loved_ones:
        trigger = "spent time with loved ones today"
    elif meaningful_actions.took_care_of_mental_health:
        trigger = "took care of their mental health today"
    elif daily_log.study_hours >= 1:
        trigger = f"put in {daily_log.study_hours} hours of study today"
    else:
        trigger = "showed up and logged their day"

    prompt = f"""
The user's name is {name}. They {trigger}. Their priorities are {priorities_text}.

Write ONE short motivational message — 1 to 2 sentences max.
Use their name once naturally.
Sound like a real friend encouraging them. Simple words. No poetry.
Be specific to what they did today.
Just write the message. No labels. No quotation marks.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You write short real motivational messages like a friend. Simple words. No poetry."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=100,
        temperature=0.8,
    )

    return response.choices[0].message.content.strip()


def get_weekly_scores(logs, actions_list, journals):
    client = get_client()

    journal_text = " ".join([j.entry for j in journals]) if journals else "No journal entries this week."
    if len(journal_text) > 600:
        journal_text = journal_text[:600] + "..."

    avg_study    = round(sum(l.study_hours for l in logs) / len(logs), 1) if logs else 0
    avg_sleep    = round(sum(l.sleep_hours for l in logs) / len(logs), 1) if logs else 0
    avg_activity = round(sum(l.physical_activity_minutes for l in logs) / len(logs), 1) if logs else 0
    avg_mood     = round(sum(l.mood for l in logs) / len(logs), 1) if logs else 0
    avg_screen   = round(sum(l.screen_time_hours for l in logs) / len(logs), 1) if logs else 0
    exercise_days   = sum(1 for a in actions_list if a.exercised)
    helped_days     = sum(1 for a in actions_list if a.helped_someone)
    quality_days    = sum(1 for a in actions_list if a.quality_time_with_loved_ones)
    discipline_days = sum(1 for a in actions_list if a.avoided_bad_habit)

    prompt = f"""
Generate a weekly life score report based on this data:
- Days logged: {len(logs)} out of 7
- Average study hours per day: {avg_study}
- Average sleep hours per day: {avg_sleep}
- Average physical activity per day: {avg_activity} minutes
- Average mood: {avg_mood}/10
- Average screen time: {avg_screen} hours per day
- Days exercised: {exercise_days}
- Days helped someone: {helped_days}
- Days quality time with loved ones: {quality_days}
- Days avoided bad habit: {discipline_days}

Journal summary: {journal_text}

Return ONLY a valid JSON object with exactly these keys:
{{
  "learning_score": 7.5,
  "health_score": 6.0,
  "discipline_score": 8.0,
  "relationships_score": 5.5,
  "consistency_score": 7.0,
  "summary": "2-3 sentence honest weekly summary in simple friendly language."
}}

All scores between 0.0 and 10.0.
Return only valid JSON. No extra text. No markdown.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You generate weekly life scores as JSON. Return only valid JSON, nothing else."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=400,
        temperature=0.3,
    )

    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)


def get_monthly_summary(logs, total_meaningful_hours, priorities):
    client = get_client()

    priorities_text = ', '.join(priorities) if priorities else 'life improvement'
    avg_mood    = round(sum(l.mood for l in logs) / len(logs), 1) if logs else 0
    avg_energy  = round(sum(l.energy_level for l in logs) / len(logs), 1) if logs else 0
    avg_sleep   = round(sum(l.sleep_hours for l in logs) / len(logs), 1) if logs else 0
    total_study = round(sum(l.study_hours for l in logs), 1)

    prompt = f"""
Write a short monthly summary for someone with these stats:
- Days logged: {len(logs)}
- Total meaningful hours: {total_meaningful_hours:.1f}
- Total study hours: {total_study}
- Average mood: {avg_mood}/10
- Average energy: {avg_energy}/10
- Average sleep: {avg_sleep} hours per night
- Their priorities: {priorities_text}

3 sentences max. Talk like a real friend. Simple words.
Mention something specific from the numbers.
End with one encouraging sentence about next month.
No poetry.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You write short friendly monthly life summaries. Simple words. Talk like a real person."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=200,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()


def get_health_suggestion(age, activity_level, avg_sleep, workout_days, recent_workouts=None):
    client = get_client()

    workout_context = ""
    if recent_workouts:
        workout_lines = []
        for w in recent_workouts:
            workout_lines.append(f"- {w.get_workout_type_display()} for {w.duration_minutes} mins ({w.get_intensity_display()})")
        workout_context = "Recent workouts:\n" + "\n".join(workout_lines)

    prompt = f"""
Give health advice to someone with these details:
- Age: {age}
- Activity level: {activity_level}
- Average sleep: {avg_sleep} hours per night
- Workout days per week: {workout_days}

{workout_context}

Give 3 simple practical health tips.
If they logged recent workouts, comment on what they did and suggest what they are missing.
For example if they only do cardio suggest strength training.
If they only do strength training suggest stretching or cardio.
Talk like a friend giving real advice. Simple words. No medical jargon.
Be specific to their actual workouts.
Write as 3 flowing sentences. No bullet points. No numbering.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You give simple friendly health advice based on actual workout data. Talk like a real person."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=250,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()
def get_future_self_message(life_setup, weekly_report=None):
    client = get_client()

    priorities_text = ', '.join(life_setup.priorities) if life_setup.priorities else 'life improvement'
    years_remaining = life_setup.years_remaining

    context = ""
    if weekly_report:
        context = f"Recent scores — Learning: {weekly_report.learning_score}, Health: {weekly_report.health_score}, Discipline: {weekly_report.discipline_score}."

    prompt = f"""
Write a short message from this person's future self.
They are {life_setup.current_age} years old with {years_remaining} years ahead.
Their priorities: {priorities_text}.
{context}

2 to 3 sentences max.
Sound like a real person — warm, honest, encouraging.
Not fear based. Hope and purpose based.
Simple words. No poetry.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You write short motivational messages from someone's future self. Warm, real, simple language."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=150,
        temperature=0.85,
    )

    return response.choices[0].message.content.strip()