from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from .forms import TweetForm
from .models import Like, Tweet


class HomeView(LoginRequiredMixin, ListView):
    model = Tweet
    template_name = "tweets/home.html"
    ordering = "created_at"
    context_object_name = "tweet_list"
    queryset = Tweet.objects.select_related("user").all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["liked_list"] = Like.objects.filter(user=self.request.user).values_list("tweet", flat=True)
        return context


class TweetCreateView(LoginRequiredMixin, CreateView):
    model = Tweet
    template_name = "tweets/create.html"
    form_class = TweetForm
    success_url = reverse_lazy("tweets:home")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TweetDetailView(LoginRequiredMixin, DetailView):
    model = Tweet
    template_name = "tweets/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["liked_list"] = Like.objects.filter(user=self.request.user).values_list("tweet", flat=True)
        return context


class TweetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Tweet
    template_name = "tweets/delete.html"
    success_url = reverse_lazy("tweets:home")

    def test_func(self, **kwargs):
        tweet = self.get_object()
        return tweet.user == self.request.user


class LikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        tweet = get_object_or_404(Tweet, pk=self.kwargs["pk"])
        Like.objects.get_or_create(user=self.request.user, tweet=tweet)
        context = {
            "liked_count": tweet.like_tweet.count(),
            "tweet_id": tweet.id,
            "is_liked": True,
        }
        return JsonResponse(context)


class UnlikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        tweet = get_object_or_404(Tweet, pk=kwargs["pk"])
        Like.objects.filter(user=self.request.user, tweet=tweet).delete()
        context = {
            "liked_count": tweet.like_tweet.count(),
            "tweet_id": tweet.id,
            "is_liked": False,
        }
        return JsonResponse(context)
