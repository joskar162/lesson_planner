from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm
from .models import LessonPlan

@login_required
def index(request):
    lesson_plan_text = None
    if request.method == "POST":
        subject = request.POST.get("subject", "").strip()
        grade = request.POST.get("grade", "").strip()
        topic = request.POST.get("topic", "").strip()
        duration = request.POST.get("duration", "").strip()
        teacher_actions = request.POST.get("teacher_actions", "").strip()

        if not (subject and grade and topic and duration):
            messages.error(request, "All fields are required.")
        else:
            try:
                duration_int = int(duration)
            except ValueError:
                duration_int = None
                messages.error(request, "Duration must be a number.")

            if duration_int is not None:
                # Build plan and include teacher actions section
                lesson_plan_text = (
                    f"Subject: {subject}\n"
                    f"Grade: {grade}\n"
                    f"Topic: {topic}\n"
                    f"Duration: {duration_int} minutes\n\n"
                    "Objective:\n"
                    f"- Students will learn the basics of {topic}.\n\n"
                    "Materials:\n"
                    "- Whiteboard, markers, worksheets.\n\n"
                    "Activities (with teacher actions):\n"
                    "1. Introduction (10 min): Hook + objectives.\n"
                    f"   Teacher actions: {teacher_actions or 'Introduce topic, set objectives.'}\n\n"
                    "2. Teaching & Modelling:\n"
                    f"   Teacher actions: {teacher_actions or 'Explain and model examples.'}\n\n"
                    "3. Guided Practice:\n"
                    f"   Teacher actions: {teacher_actions or 'Guide students through examples.'}\n\n"
                    "4. Independent Practice:\n"
                    f"   Teacher actions: {teacher_actions or 'Monitor and support.'}\n\n"
                    "5. Assessment & Plenary:\n"
                    f"   Teacher actions: {teacher_actions or 'Give quick quiz and recap.'}\n\n"
                    "Homework:\n"
                    f"- Practice problems on {topic}."
                )

                LessonPlan.objects.create(
                    user=request.user,
                    subject=subject,
                    grade=grade,
                    topic=topic,
                    duration=duration_int,
                    content=lesson_plan_text,
                    teacher_actions=teacher_actions,
                )
                messages.success(request, "Lesson plan generated and saved.")

    recent_plans = LessonPlan.objects.filter(user=request.user).order_by("-created")[:10]
    return render(request, "index.html", {"lesson_plan": lesson_plan_text, "recent_plans": recent_plans})

def welcome(request):
    return render(request, 'welcome.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()                      # saves user with hashed password
            messages.success(request, "Account created. Please log in.")
            return redirect('login')         # go to login page after register
        else:
            messages.error(request, "Registration failed. Fix the errors below.")
            print("Registration errors:", form.errors)  # check runserver console
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('welcome')

