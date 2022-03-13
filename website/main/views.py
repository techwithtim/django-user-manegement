from django.shortcuts import render, redirect
from .forms import RegisterForm, PostForm
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth import authenticate, logout, login
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Permission, Group
from django.contrib import messages
from .models import Post

'''
user = authenticate(request, username=username, password=password)
if user is not None:
    login(request, user)
    # Redirect to a success page.
    ...
else:
    # Return an 'invalid login' error message.
'''


def get_user_permissions(user):
    if user.is_superuser:
        return Permission.objects.all()
    return user.user_permissions.all() | Permission.objects.filter(group__user=user)


@login_required(login_url='/login')
def home(request):
    if request.method == "POST":
        post_id = request.POST.get("delete")
        post = Post.objects.filter(id=post_id).first()
        user_to_ban = request.POST.get("ban")
        if post and (request.user.has_perm("main.delete_post") or request.user == post.author):
            post.delete()
        elif user_to_ban and request.user.is_staff:
            user = User.objects.get(username=user_to_ban)
            if user.is_staff:
                messages.error(request, "You cannot ban this user.")
            else:
                group = Group.objects.get(name='default')
                group.user_set.remove(user)
                messages.success(request, "User banned!")

    return render(request, "main/home.html", {"posts": Post.objects.all(), "request": request})


def sign_up(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            messages.success(request, "Account Created!")
            login(request, user)
            return redirect("/home")
    else:
        form = RegisterForm()

    return render(request, "main/sign-up.html", {"form": form})


@login_required(login_url='/login')
@permission_required("main.add_post", login_url="/login", raise_exception=True)
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Post Created!")
            return redirect("/home")
    else:
        form = PostForm()

    return render(request, "main/create-post.html", {"form": form})
