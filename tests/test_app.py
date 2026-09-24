import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db"), "SECRET_KEY": "test"})
    return app.test_client()


def register(client, email, name):
    return client.post("/register", data={"email": email, "password": "secret1", "full_name": name})


def test_register_edit_and_rank(client):
    register(client, "a@x.mn", "Бат")
    client.post("/profile", data={"full_name": "Бат", "specialty": "Геологич", "years": "20",
                                  "academic": "doctor", "professional": "consulting"})
    client.post("/profile/projects", data={"name": "ТЭЗҮ", "deposit": "Оюу толгой",
                                           "size": "large", "complexity": "complex"})
    client.post("/profile/skills", data={"name": "Surpac", "level": "advanced"})
    client.get("/logout")

    register(client, "b@x.mn", "Дорж")
    client.get("/logout")

    page = client.get("/").get_data(as_text=True)
    assert page.index("Бат") < page.index("Дорж")
    # 10 + 10 + 9/30*40 + 3/15*40 = 20 + 12 + 8 = 40
    assert "40.0" in page


def test_software_filter(client):
    register(client, "a@x.mn", "Бат")
    client.post("/profile/skills", data={"name": "ArcGIS", "level": "beginner"})
    client.get("/logout")
    register(client, "b@x.mn", "Дорж")
    page = client.get("/?software=ArcGIS").get_data(as_text=True)
    assert "Бат" in page and "Дорж" not in page


def test_cannot_delete_others_project(client):
    register(client, "a@x.mn", "Бат")
    client.post("/profile/projects", data={"name": "Төсөл А", "size": "small", "complexity": "simple"})
    client.get("/logout")
    register(client, "b@x.mn", "Дорж")
    client.post("/profile/projects/1/delete")
    assert "Төсөл А" in client.get("/engineer/1").get_data(as_text=True)


def test_duplicate_email_and_login(client):
    register(client, "a@x.mn", "Бат")
    client.get("/logout")
    assert "бүртгэл үүссэн" in register(client, "a@x.mn", "Өөр").get_data(as_text=True)
    resp = client.post("/login", data={"email": "a@x.mn", "password": "wrong"})
    assert "буруу" in resp.get_data(as_text=True)
    assert client.post("/login", data={"email": "a@x.mn", "password": "secret1"}).status_code == 302


def test_profile_requires_login(client):
    assert client.get("/profile").status_code == 302


def test_english(client):
    client.get("/lang/en")
    assert "Mongolian Mining Engineers" in client.get("/").get_data(as_text=True)
