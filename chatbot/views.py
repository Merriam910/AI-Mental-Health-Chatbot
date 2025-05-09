# views.py
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json
from .chatbot_core import chat_with_blenderbot
from .models import Conversation, Session, Message,Feedback,Report
from django.core.mail import send_mail
from .forms import ContactForm
import random
import string

User = get_user_model()


# --- Main frontend views ---
def home(request):
    return render(request, 'chatbot/index.html')


@login_required
def chat_page(request):
    return render(request, 'chatbot/chat.html')


def about_us(request):
    return render(request, 'chatbot/aboutus.html')


def ai_page(request):
    return render(request, 'chatbot/ai-powered.html')


def private_page(request):
    return render(request, 'chatbot/private.html')


def effortless_page(request):
    return render(request, 'chatbot/effortless.html')


def lm_page(request):
    return render(request, 'chatbot/learnmore.html')


def report_page(request):
    return render(request, 'chatbot/contact.html')


# --- Chatbot API view ---
@csrf_exempt
@login_required
def chat_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': 'Message is empty'}, status=400)

        # ✅ Get or create active session
        session_id = request.session.get('active_session_id')
        session = None

        if session_id:
            try:
                session = Session.objects.get(pk=session_id, user=request.user)
            except Session.DoesNotExist:
                session = None

        if not session:
            session = Session.objects.create(
                user=request.user,
                start_time=timezone.now()
            )
            request.session['active_session_id'] = session.session_id

        # ✅ Use or create conversation linked to session
        conversation = session.conversation
        if not conversation:
            conversation = Conversation.objects.create(
                user=request.user,
                start_time=timezone.now()
            )
            session.conversation = conversation
            session.save()

        # ✅ Save user message
        Message.objects.create(
            conversation=conversation,
            sender='user',
            content=user_message
        )

        # ✅ Generate bot response
        bot_response = chat_with_blenderbot(user_message)

        # ✅ Save bot message
        Message.objects.create(
            conversation=conversation,
            sender='bot',
            content=bot_response
        )

        return JsonResponse({'response': bot_response})


# --- SIGNUP VIEW ---
def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')

        if User.objects.filter(email=email).exists():
            messages.error(request, "User with this email already exists!")
            return redirect('signup')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

        base_username = "user"
        counter = 1
        while User.objects.filter(username=f"{base_username}{counter}").exists():
            counter += 1
        generated_username = f"{base_username}{counter}"

        user = User.objects.create_user(
            username=generated_username,
            email=email,
            password=password,
            first_name=first_name
        )

        login(request, user)

        session = Session.objects.create(
            user=user,
            start_time=timezone.now()
        )
        request.session['active_session_id'] = session.session_id

        messages.success(request, f"Account created! Your username is {generated_username}.")
        return redirect('chat_page')

    return render(request, 'chatbot/signup.html')


# --- LOGIN VIEW ---
def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)

            if user is not None:
                login(request, user)

                # Create new session
                session = Session.objects.create(
                    user=user,
                    start_time=timezone.now()
                )
                request.session['active_session_id'] = session.session_id

                # Create new conversation and properly link it to the session
                conversation = Conversation.objects.create(
                    user=user,
                    start_time=timezone.now()
                )
                
                # Update the session with the conversation (this was the missing piece)
                Session.objects.filter(pk=session.pk).update(conversation=conversation)
                
                # Refresh the session object to get the updated version
                session.refresh_from_db()

                messages.success(request, "Login successful!")
                return redirect('chat_page')
            else:
                messages.error(request, "Incorrect password. Please try again.")

        except User.DoesNotExist:
            messages.error(request, "User does not exist. Please register first.")

    return render(request, 'chatbot/login.html')
# --- LOGOUT VIEW ---
def logout_view(request):
    if request.user.is_authenticated:
        # End conversation (if any)
        last_convo = Conversation.objects.filter(user=request.user, end_time__isnull=True).order_by('-start_time').first()
        if last_convo:
            last_convo.end_time = timezone.now()  # Same end time as the session
            last_convo.save()

        # End session (even if no conversation)
        session_id = request.session.get('active_session_id')
        if session_id:
            try:
                session = Session.objects.get(pk=session_id, user=request.user)
                if not session.end_time:
                    session.end_time = timezone.now()
                    session.save()
            except Session.DoesNotExist:
                pass

    logout(request)
    return redirect('home')


# --- End Conversation API ---
@require_POST
@login_required
def end_conversation(request):
    try:
        # End conversation (if active)
        last_convo = Conversation.objects.filter(user=request.user, end_time__isnull=True).order_by('-start_time').first()
        if last_convo:
            last_convo.end_time = timezone.now()  # Set the same end time as session
            last_convo.save()

        # End session (even if no conversation started)
        session_id = request.session.get('active_session_id')
        if session_id:
            try:
                session = Session.objects.get(pk=session_id, user=request.user)
                if not session.end_time:
                    session.end_time = timezone.now()
                    session.save()
            except Session.DoesNotExist:
                pass

        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# --- End Session On Close API ---
@csrf_exempt
@require_POST
def end_session_on_close(request):
    session_id = request.session.get('active_session_id')
    user = request.user if request.user.is_authenticated else None

    if session_id and user:
        try:
            session = Session.objects.get(pk=session_id, user=user)
            if not session.end_time:
                session.end_time = timezone.now()
                session.save()

            # Also end conversation if active
            last_convo = Conversation.objects.filter(user=user, end_time__isnull=True).order_by('-start_time').first()
            if last_convo:
                last_convo.end_time = timezone.now()  # Set the same end time as the session
                last_convo.save()
                
        except Session.DoesNotExist:
            pass

    return JsonResponse({'status': 'ok'})


@require_POST
@login_required
def submit_feedback(request):
    try:
        session_id = request.session.get('active_session_id')
        if not session_id:
            return JsonResponse({'status': 'error', 'message': 'No session found'}, status=400)

        # Get the session for the authenticated user
        session = Session.objects.get(session_id=session_id, user=request.user)

        # Ensure a conversation is linked to the session
        conversation = session.conversation
        if not conversation:
            return JsonResponse({
                'status': 'error',
                'message': 'Feedback not allowed. No conversation linked to session.'
            }, status=400)

        # Ensure the conversation has not been ended (is active)
        if conversation.end_time is not None:
            return JsonResponse({
                'status': 'error',
                'message': 'Feedback not allowed. Conversation has already ended.'
            }, status=400)

        # Ensure the user has sent at least one message in this conversation
        user_messages = Message.objects.filter(conversation=conversation, sender='user')
        if not user_messages.exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Feedback not allowed. No user messages in conversation.'
            }, status=400)

        # Parse feedback content
        data = json.loads(request.body)
        content = data.get('content', '').strip()

        # Save feedback
        Feedback.objects.create(
            user=request.user,
            session=session,
            content=content
        )

        return JsonResponse({'status': 'success'})

    except Session.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Session not found'}, status=404)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
# Report

def contact_view(request):
    success = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                # Save the report content to the database
                report = form.save()

                # Generate a unique report ID
                report_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                report.report_id = report_id
                report.save()

                print(f"Report saved with ID: {report_id}")

                # Send the confirmation email
                send_mail(
                    'Confirmation: We have received your report',
                    f"Hi {report.name},\n\nThank you for submitting your report. We have received it and will get back to you soon.\nYour report ID is: {report_id}\n\nBest regards,\nMimbot Team",
                    'aimentalhealthchatbot@gmail.com',
                    [report.email],
                    fail_silently=False,
                )

                # Render the template with success=True instead of redirecting
                return render(request, 'chatbot/contact.html', {
                    'form': form,
                    'success': True
                })
            except Exception as e:
                print(f"Error saving report: {str(e)}")
        else:
            print(form.errors)
    else:
        form = ContactForm()

    return render(request, 'chatbot/contact.html', {'form': form, 'success': success})