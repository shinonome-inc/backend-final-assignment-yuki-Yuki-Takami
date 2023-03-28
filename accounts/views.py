from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from tweets.models import Tweet

from .forms import SignUpForm
from .models import FriendShip

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
        context["is_following"] = FriendShip.objects.filter(follower=self.request.user, following=user).exists()
        context["following"] = FriendShip.objects.filter(follower=user).count()
        context["follower"] = FriendShip.objects.filter(following=user).count()
        return context


class FollowView(LoginRequiredMixin, generic.RedirectView):
    url = reverse_lazy("tweets:home")
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        follower = self.request.user
        if self.kwargs["username"] == request.user.username:
            return HttpResponseBadRequest("自分をフォローすることはできません。")
        following = get_object_or_404(User, username=self.kwargs["username"])
        if FriendShip.objects.filter(following=following, follower=follower).exists():
            return HttpResponseBadRequest("すでにフォローしています。")
        FriendShip.objects.create(follower=follower, following=following)
        return super().post(request, *args, **kwargs)


class UnFollowView(LoginRequiredMixin, generic.RedirectView):
    url = reverse_lazy("tweets:home")
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        follower = self.request.user
        if self.kwargs["username"] == request.user.username:
            return HttpResponseBadRequest("自分にリクエストできません。")
        following = get_object_or_404(User, username=self.kwargs["username"])
        FriendShip.objects.filter(follower=follower, following=following).delete()
        return super().post(request, *args, **kwargs)


class FollowingListView(LoginRequiredMixin, generic.ListView):
    model = FriendShip
    template_name = "accounts/following_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs["username"])
        context["following_list"] = (
            FriendShip.objects.select_related("following").filter(follower=user).order_by("-created_at")
        )
        return context


class FollowerListView(LoginRequiredMixin, generic.ListView):
    model = FriendShip
    template_name = "accounts/follower_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs["username"])
        context["follower_list"] = (
            FriendShip.objects.select_related("follower").filter(following=user).order_by("-created_at")
        )
        return context
