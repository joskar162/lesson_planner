from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm
from .models import LessonPlan
from django.http import HttpResponse, Http404
import io


def _make_pdf_bytes(text: str) -> bytes:
    """Return PDF bytes for the provided text using reportlab.

    Raises ImportError if reportlab is not installed.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError:
        raise

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    textobject = p.beginText(40, 750)
    textobject.setFont("Helvetica", 11)
    for line in text.splitlines():
        if len(line) <= 90:
            textobject.textLine(line)
        else:
            for i in range(0, len(line), 90):
                textobject.textLine(line[i:i+90])
    p.drawText(textobject)
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer.getvalue()


def _make_docx_bytes(text: str, lp=None) -> bytes:
    """Return DOCX bytes for the provided text. Uses python-docx.

    Raises ImportError if python-docx is not installed.
    """
    try:
        from docx import Document
    except ImportError:
        raise

    doc = Document()
    if lp is not None:
        doc.add_heading(f'Lesson Plan: {lp.topic}', level=1)
        doc.add_paragraph(f'Subject: {lp.subject}')
        doc.add_paragraph(f'Grade: {lp.grade}')
        doc.add_paragraph(f'Duration: {lp.duration} minutes')
        doc.add_paragraph('')
    for line in text.splitlines():
        if line.strip() == '':
            doc.add_paragraph('')
        else:
            doc.add_paragraph(line)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

@login_required
def index(request):
    lesson_plan_text = None
    lesson_plan_id = None
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

                lp = LessonPlan.objects.create(
                    user=request.user,
                    subject=subject,
                    grade=grade,
                    topic=topic,
                    duration=duration_int,
                    content=lesson_plan_text,
                    teacher_actions=teacher_actions,
                )
                lesson_plan_id = lp.id
                messages.success(request, "Lesson plan generated and saved.")

                # If the user clicked Generate & Download PDF/DOCX, return the generated file immediately
                if 'download_pdf' in request.POST:
                    try:
                        pdf_bytes = _make_pdf_bytes(lesson_plan_text)
                        response = HttpResponse(pdf_bytes, content_type='application/pdf')
                        response['Content-Disposition'] = f'attachment; filename="lessonplan_{lp.id}.pdf"'
                        response['Content-Length'] = str(len(pdf_bytes))
                        return response
                    except ImportError:
                        # Fallback: return plain text file with only the generated part
                        txt = lesson_plan_text or ''
                        txt_bytes = txt.encode('utf-8')
                        response = HttpResponse(txt_bytes, content_type='text/plain; charset=utf-8')
                        response['Content-Disposition'] = f'attachment; filename="lessonplan_{lp.id}.txt"'
                        response['Content-Length'] = str(len(txt_bytes))
                        return response

                if 'download_docx' in request.POST:
                    try:
                        docx_bytes = _make_docx_bytes(lesson_plan_text, lp)
                        response = HttpResponse(docx_bytes, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                        response['Content-Disposition'] = f'attachment; filename="lessonplan_{lp.id}.docx"'
                        response['Content-Length'] = str(len(docx_bytes))
                        return response
                    except ImportError:
                        # Fallback to plain text attachment
                        txt = lesson_plan_text or ''
                        txt_bytes = txt.encode('utf-8')
                        response = HttpResponse(txt_bytes, content_type='text/plain; charset=utf-8')
                        response['Content-Disposition'] = f'attachment; filename="lessonplan_{lp.id}.txt"'
                        response['Content-Length'] = str(len(txt_bytes))
                        return response

    recent_plans = LessonPlan.objects.filter(user=request.user).order_by("-created")[:10]
    return render(request, "index.html", {"lesson_plan": lesson_plan_text, "recent_plans": recent_plans, "lesson_plan_id": lesson_plan_id})

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


@login_required
def lesson_pdf(request, pk):
    """Generate a PDF for the requested LessonPlan and return it as attachment.

    If reportlab is not installed, redirect back with an instructive message.
    """
    try:
        lp = LessonPlan.objects.get(pk=pk, user=request.user)
    except LessonPlan.DoesNotExist:
        raise Http404("Lesson plan not found")

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError:
        # Fallback: return plain text attachment with the lesson plan content
        txt = lp.content or ''
        txt_bytes = txt.encode('utf-8')
        response = HttpResponse(txt_bytes, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="lessonplan_{pk}.txt"'
        response['Content-Length'] = str(len(txt_bytes))
        return response

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    textobject = p.beginText(40, 750)
    textobject.setFont("Helvetica", 11)
    for line in lp.content.splitlines():
        # Basic text wrapping for very long lines
        if len(line) <= 90:
            textobject.textLine(line)
        else:
            # naive wrap: split into chunks of ~90 chars
            for i in range(0, len(line), 90):
                textobject.textLine(line[i:i+90])
    p.drawText(textobject)
    p.showPage()
    p.save()
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="lessonplan_{pk}.pdf"'
    response['Content-Length'] = str(len(pdf_bytes))
    return response



@login_required
def lesson_docx(request, pk):
    """Generate a .docx (Word) document for the requested LessonPlan and return it as attachment.

    If python-docx is not installed, redirect back with an instructive message.
    """
    try:
        lp = LessonPlan.objects.get(pk=pk, user=request.user)
    except LessonPlan.DoesNotExist:
        raise Http404("Lesson plan not found")

    try:
        from docx import Document
    except ImportError:
        # Fallback: return plain text attachment with the lesson plan content
        txt = lp.content or ''
        txt_bytes = txt.encode('utf-8')
        response = HttpResponse(txt_bytes, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="lessonplan_{pk}.txt"'
        response['Content-Length'] = str(len(txt_bytes))
        return response

    doc = Document()
    doc.add_heading(f'Lesson Plan: {lp.topic}', level=1)
    # Add metadata lines as paragraphs for better Word formatting
    doc.add_paragraph(f'Subject: {lp.subject}')
    doc.add_paragraph(f'Grade: {lp.grade}')
    doc.add_paragraph(f'Duration: {lp.duration} minutes')
    doc.add_paragraph('')
    for line in lp.content.splitlines():
        # skip empty lines to avoid excessive spacing
        if line.strip() == '':
            doc.add_paragraph('')
        else:
            doc.add_paragraph(line)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    docx_bytes = buffer.getvalue()

    response = HttpResponse(docx_bytes, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename="lessonplan_{pk}.docx"'
    response['Content-Length'] = str(len(docx_bytes))
    return response

