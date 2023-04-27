from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Like, Tweet

User = get_user_model()


class TestHomeView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:home")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpassword",
        )
        self.client.login(username="testuser", password="testpassword")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tweets/home.html")
        self.assertQuerysetEqual(
            response.context["tweet_list"],
            Tweet.objects.order_by("-created_at"),
            ordered=False,
        )


class TestTweetCreateView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:create")
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_success_post(self):
        data = {"content": "test"}
        response = self.client.post(self.url, data)
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(Tweet.objects.filter(content=data["content"]).exists())

    def test_failure_post_with_empty_content(self):
        empty_data = {"content": ""}
        response = self.client.post(self.url, empty_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.errors["content"], ["このフィールドは必須です。"])
        self.assertFalse(Tweet.objects.exists())

    def test_failure_post_with_too_long_content(self):
        long_data = {"content": "a" * 500}
        response = self.client.post(self.url, long_data)
        self.assertEquals(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.errors["content"], ["この値は 200 文字以下でなければなりません( 500 文字になっています)。"])
        self.assertFalse(Tweet.objects.exists())


class TestTweetDetailView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )
        self.client.login(username="testuser", password="testpassword")
        self.tweet = Tweet.objects.create(user=self.user, content="test_tweet")

    def test_success_get(self):
        response = self.client.get(reverse("tweets:detail", kwargs={"pk": self.tweet.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["tweet"], self.tweet)


class TestTweetDeleteView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="testuser1",
            email="test1@test.com",
            password="testpassword1",
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="test2@test.com",
            password="testpassword2",
        )
        self.client.login(username="testuser1", password="testpassword1")
        self.tweet1 = Tweet.objects.create(user=self.user1, content="test1")
        self.tweet2 = Tweet.objects.create(user=self.user2, content="test2")

    def test_success_post(self):
        self.url = reverse("tweets:delete", kwargs={"pk": self.tweet1.pk})
        response = self.client.post(self.url)
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
        )
        self.assertFalse(Tweet.objects.filter(content="test1").exists())

    def test_failure_post_with_not_exist_tweet(self):
        response = self.client.post(reverse("tweets:delete", kwargs={"pk": 500}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Tweet.objects.count(), 2)

    def test_failure_post_with_incorrect_user(self):
        response = self.client.post(reverse("tweets:delete", kwargs={"pk": self.tweet2.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Tweet.objects.count(), 1)


class TestFavoriteView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )
        self.client.login(username="testuser", password="testpassword")
        self.data = Tweet.objects.create(user=self.user, content="test.tweet")
        self.url = reverse("tweets:like", kwargs={"pk": self.data.pk})

    def test_success_post(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Like.objects.count(), 1)

    def test_failure_post_with_not_exist_tweet(self):
        response = self.client.post(reverse("tweets:like", kwargs={"pk": "999"}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Like.objects.count(), 0)

    def test_failure_post_with_favorited_tweet(self):
        Like.objects.create(tweet=self.data, user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Like.objects.count(), 1)


class TestUnfavoriteView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )
        self.client.login(username="testuser", password="testpassword")
        self.data = Tweet.objects.create(user=self.user, content="test.tweet")
        Like.objects.create(user=self.user, tweet=self.data)
        self.url = reverse("tweets:unlike", kwargs={"pk": self.data.pk})

    def test_success_post(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Like.objects.count(), 0)

    def test_failure_post_with_not_exist_tweet(self):
        response = self.client.post(reverse("tweets:like", kwargs={"pk": "999"}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Like.objects.count(), 1)

    def test_failure_post_with_unfavorited_tweet(self):
        Like.objects.filter(tweet=self.data, user=self.user).delete()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
