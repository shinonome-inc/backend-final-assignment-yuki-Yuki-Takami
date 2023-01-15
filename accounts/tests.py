from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

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
        self.assertFalse(
            User.objects.filter(username=data["username"], email=data["email"]).exists()
        )
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


class TestHomeView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:home")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class TestLoginView(TestCase):
    def test_success_get(self):
        pass

    def test_success_post(self):
        pass

    def test_failure_post_with_not_exists_user(self):
        pass

    def test_failure_post_with_empty_password(self):
        pass


class TestLogoutView(TestCase):
    def test_success_get(self):
        pass


class TestUserProfileView(TestCase):
    def test_success_get(self):
        pass


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
    def test_success_post(self):
        pass

    def test_failure_post_with_not_exist_user(self):
        pass

    def test_failure_post_with_self(self):
        pass


class TestUnfollowView(TestCase):
    def test_success_post(self):
        pass

    def test_failure_post_with_not_exist_tweet(self):
        pass

    def test_failure_post_with_incorrect_user(self):
        pass


class TestFollowingListView(TestCase):
    def test_success_get(self):
        pass


class TestFollowerListView(TestCase):
    def test_success_get(self):
        pass
