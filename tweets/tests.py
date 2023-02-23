from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Tweet

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


class TestTweetCreateView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:create")
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
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

    def test_failure_post_with_too_long_content(self):
        long_data = {"content": "a" * 500}
        response = self.client.post(self.url, long_data)
        self.assertEquals(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(
            form.errors["content"], ["この値は 200 文字以下でなければなりません( 500 文字になっています)。"]
        )
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
        response = self.client.get(
            reverse("tweets:detail", kwargs={"pk": self.tweet.pk})
        )
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
        response = self.client.post(
            reverse("tweets:delete", kwargs={"pk": self.tweet2.pk})
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Tweet.objects.count(), 2)


class TestFavoriteView(TestCase):
    def test_success_post(self):
        pass

    def test_failure_post_with_not_exist_tweet(self):
        pass

    def test_failure_post_with_favorited_tweet(self):
        pass


class TestUnfavoriteView(TestCase):
    def test_success_post(self):
        pass

    def test_failure_post_with_not_exist_tweet(self):
        pass

    def test_failure_post_with_unfavorited_tweet(self):
        pass
