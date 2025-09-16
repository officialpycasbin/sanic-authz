import casbin
import pytest
from sanic import Sanic, response
from pathlib import Path
import uuid

from sanic_authz.middleware import CasbinAuthMiddleware


TESTS_DIR = Path(__file__).parent


@pytest.fixture
def app():
    sanic_app = Sanic(f"test_casbin_app_{uuid.uuid4()}")

    model_path = str(TESTS_DIR / "authz_model.conf")
    policy_path = str(TESTS_DIR / "authz_policy.csv")
    enforcer = casbin.Enforcer(model_path, policy_path)

    CasbinAuthMiddleware(sanic_app, enforcer)

    @sanic_app.route("/")
    async def index(request):
        return response.text("welcome")

    @sanic_app.route("/data1", methods=["GET", "POST"])
    async def data1(request):
        return response.text("data1")

    @sanic_app.route("/data2", methods=["GET", "POST", "DELETE"])
    async def data2(request):
        return response.text("data2")

    return sanic_app


def test_anonymous_user_denied(app):
    client = app.test_client
    request, response = client.get("/data1")
    assert response.status_code == 403  # Forbidden
    assert "Access Denied" in response.text


def test_authorized_user_alice_allowed(app):
    client = app.test_client
    headers = {"X-User": "alice"}
    request, response = client.get("/data1", headers=headers)
    assert response.status_code == 200
    assert response.text == "data1"


def test_authorized_user_alice_denied(app):
    client = app.test_client
    headers = {"X-User": "alice"}
    request, response = client.post("/data1", headers=headers)
    assert response.status_code == 403
    assert "Subject 'alice' is not authorized to perform 'POST' on '/data1'" in response.text


def test_authorized_user_bob_allowed(app):
    client = app.test_client
    headers = {"X-User": "bob"}
    request, response = client.post("/data2", headers=headers)
    assert response.status_code == 200
    assert response.text == "data2"


def test_authorized_user_bob_denied(app):
    client = app.test_client
    headers = {"X-User": "bob"}
    request, response = client.get("/data2", headers=headers)
    assert response.status_code == 403


def test_admin_user_cathy_allowed(app):
    client = app.test_client
    headers = {"X-User": "cathy"}

    request, response = client.get("/data1", headers=headers)
    assert response.status_code == 200
    assert response.text == "data1"

    request, response = client.post("/data1", headers=headers)
    assert response.status_code == 200
    assert response.text == "data1"

    request, response = client.get("/data2", headers=headers)
    assert response.status_code == 200
    assert response.text == "data2"

    request, response = client.post("/data2", headers=headers)
    assert response.status_code == 200
    assert response.text == "data2"

    request, response = client.delete("/data2", headers=headers)
    assert response.status_code == 200
    assert response.text == "data2"

    request, response = client.get("/", headers=headers)
    assert response.status_code == 200
    assert response.text == "welcome"
