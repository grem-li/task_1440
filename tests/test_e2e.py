import requests


app_url = "http://127.0.0.1:8080"


class TestGenerate:
    def test_secret_generate_get(self):
        """
        Невалидный GET-запрос /generate (405 Method Not Allowed)
        """
        req_session = requests.Session()
        resp = req_session.get(f"{app_url}/generate")
        assert resp.status_code == 405

    def test_secret_generate_post_ok(self):
        """
        Отправка валидного POST-запроса /generate с кодом 200
        Текстовый ответ с secret_key
        """
        req_session = requests.Session()
        resp = req_session.post(f"{app_url}/generate", json={"secret": "string", "pwd": "string"})
        assert resp.status_code == 200
        assert "content-type" in resp.headers and resp.headers["content-type"] == "text/html; charset=utf-8"
        assert len(resp.text) == 24

    def test_secret_generate_invalid_json(self):
        """
        Отправка невалидного json-а /generate (422 Unprocessable Entity)
        """
        resp = requests.post(f"{app_url}/generate",
                             data='{"secrring", "secret", "pwd": "stinag"',
                             headers={"Content-Type": "application/json"})
        assert resp.status_code == 422

    def test_secret_generate_double_requests(self):
        """
        Отправка двух одинаковых POST-запросов /generate
        Два ответа с разными secret_key
        """
        resp1 = requests.post(f"{app_url}/generate", json={"secret": "string", "pwd": "string"})
        resp2 = requests.post(f"{app_url}/generate", json={"secret": "string", "pwd": "string"})
        assert resp1.status_code == resp2.status_code == 200
        assert len(resp1.text) == len(resp2.text) == 24
        assert resp1.text != resp2.text


class TestSecrets:
    def test_secret_recieve_ok(self):
        """
        Отправка валидного POST-запроса /secrets/... с правельным паролем
        Валиднвй ответ
        """
        req_session = requests.Session()
        resp1 = req_session.post(f"{app_url}/generate", json={"secret": "string", "pwd": "string"})
        resp2 = req_session.post(f"{app_url}/secrets/{resp1.text}", json={"pwd": "string"})
        assert resp2.status_code == 200
        assert "content-type" in resp2.headers and resp2.headers["content-type"] == "text/html; charset=utf-8"
        assert resp2.text == "string"

    def test_secret_recieve_err(self):
        """
        Отправка POST-запроса /secrets/... с несуществующим ключом
        Ответ 404 Not Found
        """
        resp = requests.post(f"{app_url}/secrets/abc12345678", json={"pwd": "string"})
        assert resp.status_code == 404

    def test_secret_double_recieve(self):
        """
        Отправка валидного POST-запроса /secrets/... дважды
        Валиднвй первый ответ и 404 на второй
        """
        req_session = requests.Session()
        resp1 = req_session.post(f"{app_url}/generate", json={"secret": "string", "pwd": "string"})
        resp2 = req_session.post(f"{app_url}/secrets/{resp1.text}", json={"pwd": "string"})
        resp3 = req_session.post(f"{app_url}/secrets/{resp1.text}", json={"pwd": "string"})
        assert resp2.status_code == 200
        assert resp3.status_code == 404

    def test_secret_recieve_no_pwd(self):
        """
        Отправка POST-запроса /secrets/... без пароля (422 Unprocessable Entity)
        """
        req_session = requests.Session()
        resp1 = req_session.post(f"{app_url}/generate", json={"secret": "string", "pwd": "string"})
        resp2 = req_session.post(f"{app_url}/secrets/{resp1.text}", json={})
        assert resp2.status_code == 422

    def test_secret_recieve_invalid_pwd(self):
        """
        Отправка POST-запроса /secrets/... с невалидным паролем (403 Forbidden)
        Пару раз можно попробовать еще, на 4й секрет удаляется (404 Not Found)
        """
        req_session = requests.Session()
        resp1 = req_session.post(f"{app_url}/generate", json={"secret": "string", "pwd": "string"})
        for _ in range(4):
            resp2 = req_session.post(f"{app_url}/secrets/{resp1.text}", json={"pwd": "123456"})
            assert resp2.status_code == 403
        resp3 = req_session.post(f"{app_url}/secrets/{resp1.text}", json={"pwd": "123456"})
        assert resp3.status_code == 404
