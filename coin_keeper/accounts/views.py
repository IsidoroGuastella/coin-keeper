import time
from django.http import JsonResponse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings
from django.db.models import Q
from django.template.loader import render_to_string
from .utils import genera_token, verifica_token, validate_email_mx
from .models import Esemplare


def rate_limit(key_prefix, limit=5, period=60):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            key = f"{key_prefix}:{request.META.get('REMOTE_ADDR')}"
            history = cache.get(key, [])
            now = time.time()
            history = [t for t in history if now - t < period]
            if len(history) >= limit:
                messages.error(request, _("Troppe richieste, riprova più tardi."))
                return redirect("login")
            history.append(now)
            cache.set(key, history, timeout=period)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

User = get_user_model()

def searching(request):
    query = request.GET.get("q", "").strip()
    risultati = []

    if query:
        risultati = Esemplare.objects.filter(
            utente=request.user
        ).filter(
            Q(moneta__valore_nominale__icontains=query) |
            Q(moneta__anno_conio__icontains=query) |
            Q(moneta__stato__nome__icontains=query)
        ).order_by('moneta__valore_nominale', 'moneta__stato__nome', 'moneta__anno_conio')


    # Gestione richiesta AJAX
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string("partials/_risultati.html", {"risultati": risultati})
        return JsonResponse({"html": html})

    # Primo caricamento normale
    return render(request, "accounts/searching.html", {"risultati": risultati, "query": query})


def dashboard_view(request):
    return render(request, "accounts/dashboard.html")

def verify_view(request, token):
    user_id = verifica_token(token)
    if not user_id:
        messages.error(request, _("Link non valido o scaduto."))
        return redirect("login")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, _("Utente inesistente."))
        return redirect("login")

    if user.is_verified:
        messages.info(request, _("Email già verificata."))
    else:
        user.is_verified = True
        user.save()
        messages.success(request, _("Email verificata con successo! Ora puoi accedere."))
    
    return redirect("login")

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            if user.is_verified:
                login(request, user)
                return redirect("dashboard")
            else:
                messages.error(request, _("Devi prima verificare la tua email."))
                return redirect("login")
        else:
            messages.error(request, _("Credenziali non valide."))
            return redirect("login")

    return render(request, "accounts/login.html")

@rate_limit("signup", limit=5, period=60)
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, _("Le password non coincidono."))
            return render(request, "accounts/signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, _("Nome utente già esistente."))
            return render(request, "accounts/signup.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, _("Email già registrata."))
            return render(request, "accounts/signup.html")

        try:
            validate_email_mx(email)
        except Exception as e:
            messages.error(request, str(e))
            return render(request, "accounts/signup.html")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            is_verified=False
        )

        token = genera_token(user.id)
        verify_url = f"http://127.0.0.1:8000/accounts/verify/{token}/"

        subject = _("Verifica la tua email - Coin Keeper")
        message = _("Ciao {username}, clicca qui per verificare la tua email: {url}").format(
            username=username, url=verify_url
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list)

        messages.success(request, _("Registrazione completata! Controlla la tua email per verificare l'account."))
        return redirect("login")

    return render(request, "accounts/signup.html")

def logout_view(request):
    logout(request)
    return redirect("login")

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, _("Nessun utente registrato con questa email."))
            return redirect("password_reset_request")

        # Genera token e URL di reset
        token = genera_token(user.id)
        reset_url = f"http://127.0.0.1:8000/accounts/password-reset-confirm/{token}/"

        subject = _("Recupero password - Coin Keeper")
        message = _("Clicca qui per reimpostare la tua password: {url}").format(url=reset_url)

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

        messages.success(request, _("Ti abbiamo inviato un'email con le istruzioni per reimpostare la password."))
        return redirect("login")

    return render(request, "accounts/password_reset_request.html")

def password_reset_confirm(request, token):
    user_id = verifica_token(token)
    if not user_id:
        messages.error(request, _("Link non valido o scaduto."))
        return redirect("login")

    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, _("Le password non coincidono."))
            return redirect("password_reset_confirm", token=token)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, _("Utente inesistente."))
            return redirect("login")

        user.set_password(password1)
        user.save()
        messages.success(request, _("Password aggiornata con successo! Ora puoi accedere."))
        return redirect("login")

    return render(request, "accounts/password_reset_confirm.html", {"token": token})
