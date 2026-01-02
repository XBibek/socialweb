from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import LoginForm, UserRegistrationForm, \
                    UserEditForm ,ProfileEditForm
from django.contrib.auth.decorators import login_required
from .models import Profile, Contact
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from actions.utilis import create_action
from actions.models import Action

# Create your views here.
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username = cd['username'],
                                password = cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated Successfully')
                else:
                    return HttpResponse('Invalid Login')
            else:
                return HttpResponse('Invalid Login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html',{'form':form})


@login_required
def dashboard(request):
    #display all actions by default
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id',
                                                       flat=True)
    if following_ids:
        #If user is following others, retrieve only their actions
        actions = actions.filter(user_id__in=following_ids)
    actions = actions.select_related('user', 'user__profile')\
                     .prefetch_related('target')[:10]
    return render(request,
                  'account/dashboard.html',
                  {'section': 'dashboard',
                   'actions': actions})



# def user_logout(request):
#     logout(request)
#     return render(request, 'account/logged_out.html')

# @login_required
# def password_change(request):
#     if request.method == 'POST':
#         old_password = request.POST.get('old_password', '')
#         new_password1 = request.POST.get('new_password1', '')
#         new_password2 = request.POST.get('new_password2', '')
        
#         user = request.user
        
#         # Check old password
#         if not user.check_password(old_password):
#             return render(request, 'registration/password_change_form.html', 
#                          {'error': 'Old password is incorrect'})
        
#         # Check if new passwords match
#         if new_password1 != new_password2:
#             return render(request, 'registration/password_change_form.html',
#                          {'error': 'New passwords do not match'})
        
#         # Check if new password is not empty
#         if not new_password1:
#             return render(request, 'registration/password_change_form.html',
#                          {'error': 'New password cannot be empty'})
        
#         # Set the new password
#         user.set_password(new_password1)
#         user.save()
#         update_session_auth_hash(request, user)
#         return redirect('password_change_done')
    
#     return render(request, 'registration/password_change_form.html')



# def password_change_done(request):
#     return render(request, 'registration/password_change_done.html')

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            #Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            #Set the chosen password
            new_user.set_password(
                user_form.cleaned_data['password'])
            #Save the User_object
            new_user.save()
            #Create the user profile
            Profile.objects.create(user=new_user)
            create_action(new_user, 'has created an account')
            return render(request,
                          'account/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'account/register.html',
                  {'user_form' : user_form})

@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                                       data=request.POST,
                                       files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated' \
                             'successfully')
            return redirect('dashboard')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(request,
                  'account/edit.html',
                  {'user_form' : user_form,
                   'profile_form': profile_form})
    

@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request,
                  'account/user/list.html',
                  {'section': 'people',
                   'users': users})

@login_required
def user_detail(request, username):
    user = get_object_or_404(User,
                             username=username,
                             is_active=True)
    return render(request,
                  'account/user/detail.html',
                  {'section':'people',
                   'user':user})


@login_required
@require_POST
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(
                    user_from=request.user,
                    user_to=user
                )
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(
                    user_from=request.user,
                    user_to=user
                ).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})