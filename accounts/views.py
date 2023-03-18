from django.contrib.auth import authenticate, login
from django.views import generic
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponseBadRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from tweets.models import Tweet

from .forms import SignUpForm

User = get_user_model()


class SignUpView(generic.CreateView):
    form_class = SignUpForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("tweets:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class UserProfileView(LoginRequiredMixin, generic.DetailView):
    model = User
    template_name = "accounts/profile.html"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        context["tweet_list"] = Tweet.objects.select_related("user").filter(user=user)
        return context


class FollowView(LoginRequiredMixin, generic.RedirectView):
    url = reverse_lazy("tweets:home")
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        if self.kwargs["username"] == request.user.username:
            return HttpResponseBadRequest("自分自身をフォローすることはできません。")
        user = get_object_or_404(User, username=self.kwargs["username"])
        request.user.following.add(user)
        return super().post(request, *args, **kwargs)


class UnFollowView(LoginRequiredMixin, generic.RedirectView):
    url = reverse_lazy("tweets:home")
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        if self.kwargs["username"] == request.user.username:
            return HttpResponseBadRequest("自分自身にリクエストできません。")
        user = get_object_or_404(User, username=self.kwargs["username"])
        request.user.following.remove(user)
        return super().post(request, *args, **kwargs)


class FollowingListView(LoginRequiredMixin, generic.ListView):
    model = User
    template_name = "accounts/following_list.html"
    paginate_by = 10

    def get_queryset(self):
        self.user = User.objects.get(username=self.kwargs["username"])
        return self.user.following.all().order_by("-following_id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.user
        return context


class FollowerListView(LoginRequiredMixin, generic.ListView):
    model = User
    template_name = "views/follower_list.html"
    paginate_by = 10

    def get_queryset(self):
        self.user = User.objects.get(username=self.kwargs["username"])
        return self.user.followed_by.all().order_by("-last_login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.user
        return context
