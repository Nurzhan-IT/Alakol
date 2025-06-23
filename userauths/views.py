from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from userauths.models import User, Profile
from userauths.forms import UserRegisterForm
from userauths.utils import save_registration_consents

# Create your views here.

def RegisterView(request, *args, **kwargs):
    if request.user.is_authenticated:
        messages.warning(request, _("Hey %(username)s, you are already logged in") % {'username': request.user.username})
        return redirect('hotel:index')   

    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        with transaction.atomic():
            user = form.save()
            full_name = form.cleaned_data.get('full_name')
            phone = form.cleaned_data.get('phone')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')

            email = email.lower()

            user = authenticate(email=email, password=password)
            login(request, user)

            messages.success(request, _("Hi %(username)s, your account have been created successfully.") % {'username': request.user.username})

            profile = user.profile
            profile.full_name = full_name
            profile.phone = phone
            profile.save(update_fields=['full_name', 'phone'])

            # Сохраняем согласия пользователя при регистрации
            consent_data = {
                'terms_consent': request.POST.get('terms_consent'),
                'privacy_consent': request.POST.get('privacy_consent'),
                'personal_data_consent': request.POST.get('personal_data_consent'),
                'marketing_consent': request.POST.get('marketing_consent'),
            }
            save_registration_consents(user, request, consent_data)

        return redirect('hotel:index')
    
    context = {'form': form}
    return render(request, 'userauths/sign-up.html', context)

def LoginView(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if email:
            email = email.lower()

        try:
            user = get_object_or_404(User, email=email)
            
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, _("You are Logged In"))
                return redirect('hotel:index')
            else:
                messages.error(request, _('Username or password does not exist.'))
        
        except User.DoesNotExist:
            messages.error(request, _('User does not exist'))

    return HttpResponseRedirect("/")

def loginViewTemp(request):
    if request.user.is_authenticated:
        messages.warning(request, _("You are already logged in"))
        return redirect('hotel:index')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if email:
            email = email.lower()

        try:
            user_exists = User.objects.filter(email=email).exists()
            
            if not user_exists:
                messages.error(request, _('User does not exist'))
                return render(request, "userauths/sign-in.html")
                
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, _("You are Logged In"))
                next_url = request.GET.get("next", 'hotel:index')
                return redirect(next_url)
            else:
                messages.error(request, _('Username or password does not exist.'))
        
        except Exception as e:
            messages.error(request, _('An error occurred during login'))

    return render(request, "userauths/sign-in.html")

def LogoutView(request):
    logout(request)
    messages.success(request, _('You have been logged out'))
    return redirect("userauths:sign-in")