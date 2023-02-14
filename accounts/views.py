from django.contrib.auth import authenticate, login
from django.views import generic
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from .forms import SignUpForm

User = get_user_model()


class SignUpView(CreateView):
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
    context_object_name = "user"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.object
        context["tweet_list"] = user.tweet_set.order_by("-created_at")

        return context
