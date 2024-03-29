from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

from tweets.models import Tweet

from .models import FriendShip

User = get_user_model()


class TestSignUpView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(User.objects.filter(username=valid_data["username"]).exists())
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_form(self):
        data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=data["username"], email=data["email"]).exists())
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["username"], ["このフィールドは必須です。"])
        self.assertEqual(form.errors["email"], ["このフィールドは必須です。"])
        self.assertEqual(form.errors["password1"], ["このフィールドは必須です。"])
        self.assertEqual(form.errors["password2"], ["このフィールドは必須です。"])

    def test_failure_post_with_empty_username(self):
        data = {
            "username": "",
            "email": "tests2@icloud.com",
            "password1": "QAz105edc",
            "password2": "QAz105edc",
        }
        response = self.client.post(self.url, data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["username"], ["このフィールドは必須です。"])

    def test_failure_post_with_empty_email(self):
        data = {
            "username": "suzuki",
            "email": "",
            "password1": "QAZ105edc",
            "password2": "QAZ105edc",
        }
        response = self.client.post(self.url, data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["email"], ["このフィールドは必須です。"])

    def test_failure_post_with_empty_password(self):
        data = {
            "username": "takahashi",
            "email": "tests3@icloud.com",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password1"], ["このフィールドは必須です。"])
        self.assertEqual(form.errors["password2"], ["このフィールドは必須です。"])

    def test_failure_post_with_duplicated_user(self):
        data = {
            "username": "yamada",
            "email": "tests4@icloud.com",
            "password1": "QaZ105edc",
            "password2": "QaZ105edc",
        }

        User.objects.create_user(
            username="yamada",
            email="tests4@icloud.com",
            password="QaZ105edc",
        )
        response = self.client.post(self.url, data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["username"], ["同じユーザー名が既に登録済みです。"])

    def test_failure_post_with_invalid_email(self):
        data = {
            "username": "ashizawa",
            "email": "tests5icloud.com",
            "password1": "Qaz105Edc",
            "password2": "Qaz105Edc",
        }
        User.objects.create_user(
            username="ashizawa",
            email="tests5icloud.com",
            password="Qaz105Edc",
        )
        response = self.client.post(self.url, data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["email"], ["有効なメールアドレスを入力してください。"])

    def test_failure_post_with_too_short_password(self):
        data = {
            "username": "yamamoto",
            "email": "tests6@icloud.com",
            "password1": "a1B",
            "password2": "a1B",
        }
        response = self.client.post(self.url, data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password2"],
            ["このパスワードは短すぎます。最低 8 文字以上必要です。"],
        )

    def test_failure_post_with_password_similar_to_username(self):
        data = {
            "username": "takedabc",
            "email": "tests7@icloud.com",
            "password1": "takedabc",
            "password2": "takedabc",
        }
        response = self.client.post(self.url, data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password2"], ["このパスワードは ユーザー名 と似すぎています。"])

    def test_failure_post_with_only_numbers_password(self):
        data = {
            "username": "saito",
            "email": "tests8@icloud.com",
            "password1": "12481632",
            "password2": "12481632",
        }
        response = self.client.post(self.url, data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password2"], ["このパスワードは数字しか使われていません。"])

    def test_failure_post_with_mismatch_password(self):
        data = {
            "username": "sakurai",
            "email": "tests9@icloud.com",
            "password1": "Qaz105edc",
            "password2": "Qaz105eee",
        }
        response = self.client.post(self.url, data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password2"], ["確認用パスワードが一致しません。"])


class TestLoginView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:login")
        self.user = User.objects.create_user(username="testuser", email="test@email.com", password="testpassword")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_success_post(self):
        data = {
            "username": "testuser",
            "password": "testpassword",
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):
        not_exist_user_data = {
            "username": "fakeuser",
            "password": "fakepassward",
        }
        response = self.client.post(self.url, not_exist_user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"][0],
            "正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。",
        )
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_password(self):
        password_empty_user_data = {
            "username": "testuser",
            "password": "",
        }
        response = self.client.post(self.url, password_empty_user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password"], ["このフィールドは必須です。"])
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestLogoutView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@email.com", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

    def test_success_get(self):
        response = self.client.get(reverse("accounts:logout"))
        self.assertRedirects(
            response,
            reverse("accounts:login"),
            status_code=302,
            target_status_code=200,
        )
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestUserProfileView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
        )
        self.client.login(username="testuser", password="testpassword")
        self.post = Tweet.objects.create(user=self.user, content="testpost")
        self.url = reverse("accounts:user_profile", kwargs={"username": self.user.username})

    def test_success_get(self):
        response = self.client.get(self.url)
        context = response.context
        self.assertQuerysetEqual(context["tweet_list"], Tweet.objects.filter(user=self.user))


class TestUserProfileEditView(TestCase):
    def test_success_get(self):
        pass

    def test_success_post(self):
        pass

    def test_failure_post_with_not_exists_user(self):
        pass

    def test_failure_post_with_incorrect_user(self):
        pass


class TestFollowView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="hoge@example.com",
            password="hogepass",
        )
        self.targetuser = User.objects.create_user(
            username="targetuser",
            email="fuga@example.com",
            password="fugapass",
        )
        self.client.force_login(self.user)

    def test_success_post(self):
        response = self.client.post(
            reverse(
                "accounts:follow",
                kwargs={"username": self.targetuser.username},
            ),
        )
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertEqual(self.user.following.count(), 0)
        self.assertEqual(self.user.following.first(), None)

    def test_failure_post_with_not_exist_user(self):
        response = self.client.post(
            reverse(
                "accounts:follow",
                kwargs={"username": "heman"},
            ),
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.user.following.count(), 0)

    def test_failure_post_with_self(self):
        response = self.client.post(
            reverse(
                "accounts:follow",
                kwargs={"username": self.user.username},
            ),
        )
        self.assertEqual(response.status_code, 400)
        form = response.content.decode("utf-8")
        expected_errs = "自分をフォローすることはできません。"
        self.assertEqual(expected_errs, form)
        self.assertEqual(self.user.following.count(), 0)


class TestUnfollowView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword")
        self.client.login(username="testuser1", password="testpassword")
        FriendShip.objects.create(follower=self.user1, following=self.user2)

    def test_success_post(self):
        response = self.client.post(reverse("accounts:unfollow", kwargs={"username": self.user2.username}))
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertFalse(FriendShip.objects.filter(follower=self.user2, following=self.user1).exists())

    def test_failure_post_with_not_exist_user(self):
        response = self.client.post(reverse("accounts:unfollow", kwargs={"username": "not_exist_user.username"}))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(FriendShip.objects.count(), 1)

    def test_failure_post_with_self(self):
        response = self.client.post(reverse("accounts:unfollow", kwargs={"username": self.user1.username}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(FriendShip.objects.count(), 1)


class TestFollowingListView(TestCase):
    def test_success_get(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("accounts:following_list", kwargs={"username": self.user.username}))
        self.assertEqual(response.status_code, 200)


class TestFollowerListView(TestCase):
    def test_success_get(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("accounts:follower_list", kwargs={"username": self.user.username}))
        self.assertEqual(response.status_code, 200)
