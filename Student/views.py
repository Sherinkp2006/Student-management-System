from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from Student.forms import AdminUserCreationForm, StudentForm
from .models import Student


def register(request):
    if request.method == 'POST':
        user_name = request.POST.get('username')
        user_pass = request.POST.get('password')
        user_pass2 = request.POST.get('password2')
        if user_name == '' or user_pass == '' or user_pass2 == '' or user_pass != user_pass2:
            messages.error(request, "Invalid username or password.")
            return render(request, 'register.html')
        elif User.objects.filter(username=user_name).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'register.html')
        try:
            if User.objects.filter(username=user_name).exists():
                messages.error(request, "That username is already taken.")
                return redirect('register')

            new_user = User(username=user_name)
            new_user.set_password(user_pass)
            new_user.save()

            messages.success(request, "Registration successful!")
            return redirect('login_page')
        except Exception as e:
            print("--- REGISTRATION ERROR DETAILS ---")
            print(e)
            print("---------------------------------")
            messages.error(request, "An error occurred during registration.")
            return redirect('register')

    return render(request, 'register.html')


def login_page(request):
    if request.method == 'POST':
        user_name = request.POST.get('username')
        user_pass = request.POST.get('password')

        user = authenticate(request, username=user_name, password=user_pass)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user_name}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'login.html')

    return render(request, 'login.html')


# --- FIXED HOME VIEW FUNCTION ---
@login_required
def home(request):
    all_students = Student.objects.all()

    # Pack the student records queryset into context
    context = {
        'all_students': all_students,
    }

    # Context variable passed explicitly as the 3rd argument to light up the counter element
    return render(request, 'home.html', context)


@login_required
def user_management(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            role = form.cleaned_data['role']
            new_user.is_staff = role in ('staff', 'superuser')
            new_user.is_superuser = role == 'superuser'
            new_user.save()
            messages.success(request, f"User '{new_user.username}' was created.")
            return redirect('user_management')
    else:
        form = AdminUserCreationForm()

    users = User.objects.order_by('username')
    context = {
        'form': form,
        'users': users,
        'user_count': User.objects.count(),
        'active_user_count': User.objects.filter(is_active=True).count(),
        'staff_count': User.objects.filter(is_staff=True).count(),
        'superuser_count': User.objects.filter(is_superuser=True).count(),
    }
    return render(request, 'user_management.html', context)


@login_required
@require_POST
def manage_user(request, user_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    action = request.POST.get('action')
    with transaction.atomic():
        managed_user = get_object_or_404(
            User.objects.select_for_update(),
            pk=user_id,
        )

        if managed_user.pk == request.user.pk:
            messages.error(request, "You cannot change or delete your own administrator account here.")
            return redirect('user_management')

        if action == 'delete':
            if (
                managed_user.is_active
                and managed_user.is_superuser
                and User.objects.filter(is_active=True, is_superuser=True).count() <= 1
            ):
                messages.error(request, "You cannot delete the last active superuser.")
                return redirect('user_management')
            username = managed_user.username
            managed_user.delete()
            messages.success(request, f"User '{username}' was deleted.")
        elif action in ('activate', 'deactivate'):
            is_active = action == 'activate'
            if (
                managed_user.is_active
                and managed_user.is_superuser
                and not is_active
                and User.objects.filter(is_active=True, is_superuser=True).count() <= 1
            ):
                messages.error(request, "You cannot deactivate the last active superuser.")
                return redirect('user_management')
            managed_user.is_active = is_active
            managed_user.save(update_fields=['is_active'])
            messages.success(
                request,
                f"User '{managed_user.username}' was {'activated' if is_active else 'deactivated'}.",
            )
        elif action == 'role':
            role = request.POST.get('role')
            if role not in ('user', 'staff', 'superuser'):
                messages.error(request, "Choose a valid account role.")
                return redirect('user_management')

            is_superuser = role == 'superuser'
            if (
                managed_user.is_active
                and managed_user.is_superuser
                and not is_superuser
                and User.objects.filter(is_active=True, is_superuser=True).count() <= 1
            ):
                messages.error(request, "You cannot remove superuser access from the last active superuser.")
                return redirect('user_management')

            managed_user.is_staff = role in ('staff', 'superuser')
            managed_user.is_superuser = is_superuser
            managed_user.save(update_fields=['is_staff', 'is_superuser'])
            messages.success(
                request,
                f"User '{managed_user.username}' was assigned the {role} role.",
            )
        else:
            messages.error(request, "Choose a valid user-management action.")

    return redirect('user_management')


@login_required
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            if 'Save_details' in request.POST:
                return redirect('home')
            elif 'Save_and_refresh' in request.POST:
                return redirect('add_student')
    else:
        form = StudentForm()
    return render(request, 'add_student.html', {'form': form})


@login_required
def list_students(request):
    all_students = Student.objects.all()
    return render(request, 'list_student.html', {'all_students': all_students})


@login_required
def update_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('list_students')
    else:
        form = StudentForm(instance=student)

    return render(request, 'update.html', {'form': form, 'student': student})


@login_required
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    return redirect('list_students')