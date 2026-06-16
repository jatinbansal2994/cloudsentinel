"""
Unit tests for lambda/api-handler/index.py.
Mocks all boto3 calls so no AWS credentials are needed.
"""
import sys
import os
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

# Set required env vars before the module loads
os.environ.setdefault("TENANT_TABLE", "test-tenants")
os.environ.setdefault("ALERT_TABLE", "test-alerts")
os.environ.setdefault("KINESIS_STREAM_NAME", "test-stream")
os.environ.setdefault("USER_POOL_ID", "us-east-1_TESTPOOL")
os.environ.setdefault("ADMIN_GROUP", "cloudsentinel-admins")

import importlib.util

API_INDEX = Path(__file__).parent.parent / "lambda" / "api-handler" / "index.py"

_mock_ddb = MagicMock()
_mock_tenant_table = MagicMock()
_mock_alert_table = MagicMock()

def _table_factory(name):
    if name == "test-tenants":
        return _mock_tenant_table
    if name == "test-alerts":
        return _mock_alert_table
    return MagicMock()

_mock_ddb.Table.side_effect = _table_factory
_mock_kinesis = MagicMock()
_mock_cognito = MagicMock()

def _client_factory(service_name, **kwargs):
    if service_name == "kinesis":
        return _mock_kinesis
    if service_name == "cognito-idp":
        return _mock_cognito
    return MagicMock()

# Use a unique module name to avoid colliding with stream-processor's index.py.
with patch("boto3.resource", return_value=_mock_ddb), \
     patch("boto3.client", side_effect=_client_factory):
    _spec = importlib.util.spec_from_file_location("api_handler_index", API_INDEX)
    ah = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(ah)


# ── helpers ────────────────────────────────────────────────────────────────────

def _event(method: str, path: str, body=None, tenant_id: str = "tenant-test",
           groups=None) -> dict:
    claims = {"custom:tenantId": tenant_id}
    if groups is not None:
        claims["cognito:groups"] = groups
    return {
        "httpMethod": method,
        "path": path,
        "body": json.dumps(body) if body else None,
        "requestContext": {"authorizer": {"claims": claims}},
    }


def _admin_event(method: str, path: str, body=None) -> dict:
    return _event(method, path, body,
                  tenant_id="tenant-admin",
                  groups=["cloudsentinel-admins"])


def _parse_body(response: dict) -> dict:
    return json.loads(response["body"])


# ── respond() and routing ──────────────────────────────────────────────────────

class TestRouting:
    def test_unknown_route_returns_404(self):
        event = _event("GET", "/nonexistent")
        res = ah.handler(event, None)
        assert res["statusCode"] == 404

    def test_cors_header_always_present(self):
        _mock_alert_table.query.return_value = {"Items": []}
        event = _event("GET", "/alerts")
        res = ah.handler(event, None)
        assert res["headers"]["Access-Control-Allow-Origin"] == "*"


# ── is_admin() ─────────────────────────────────────────────────────────────────

class TestIsAdmin:
    def test_admin_group_as_list(self):
        assert ah.is_admin({"cognito:groups": ["cloudsentinel-admins"]}) is True

    def test_admin_group_as_string(self):
        assert ah.is_admin({"cognito:groups": "cloudsentinel-admins"}) is True

    def test_non_admin_group(self):
        assert ah.is_admin({"cognito:groups": ["some-other-group"]}) is False

    def test_no_groups_key(self):
        assert ah.is_admin({}) is False

    def test_empty_group_list(self):
        assert ah.is_admin({"cognito:groups": []}) is False


# ── GET /alerts ────────────────────────────────────────────────────────────────

class TestGetAlerts:
    def test_returns_alerts_list(self):
        _mock_alert_table.query.return_value = {
            "Items": [
                {"alertId": "a1", "tenantId": "tenant-test",
                 "severity": "high", "score": "0.05", "createdAt": "2026-01-01T00:00:00Z"}
            ]
        }
        event = _event("GET", "/alerts")
        res = ah.handler(event, None)
        assert res["statusCode"] == 200
        body = _parse_body(res)
        assert "alerts" in body
        assert len(body["alerts"]) == 1
        assert body["alerts"][0]["alertId"] == "a1"

    def test_empty_alerts_returns_empty_list(self):
        _mock_alert_table.query.return_value = {"Items": []}
        event = _event("GET", "/alerts")
        res = ah.handler(event, None)
        assert res["statusCode"] == 200
        assert _parse_body(res)["alerts"] == []

    def test_queries_only_own_tenant(self):
        _mock_alert_table.query.return_value = {"Items": []}
        event = _event("GET", "/alerts", tenant_id="tenant-xyz")
        ah.handler(event, None)
        call_kwargs = _mock_alert_table.query.call_args.kwargs
        assert ":t" in call_kwargs["ExpressionAttributeValues"]
        assert call_kwargs["ExpressionAttributeValues"][":t"] == "tenant-xyz"


# ── GET /tenants ───────────────────────────────────────────────────────────────

class TestGetTenant:
    def test_returns_tenant_config(self):
        _mock_tenant_table.get_item.return_value = {
            "Item": {"tenantId": "tenant-test", "sk": "CONFIG", "name": "Test Corp", "plan": "pro"}
        }
        event = _event("GET", "/tenants")
        res = ah.handler(event, None)
        assert res["statusCode"] == 200
        body = _parse_body(res)
        assert body["tenant"]["name"] == "Test Corp"

    def test_returns_empty_tenant_when_not_found(self):
        _mock_tenant_table.get_item.return_value = {}
        event = _event("GET", "/tenants")
        res = ah.handler(event, None)
        assert res["statusCode"] == 200
        assert _parse_body(res)["tenant"] == {}


# ── POST /tenants ──────────────────────────────────────────────────────────────

class TestCreateTenant:
    def test_creates_tenant_returns_201(self):
        _mock_tenant_table.put_item.return_value = {}
        event = _event("POST", "/tenants", body={"name": "Acme", "plan": "free"})
        res = ah.handler(event, None)
        assert res["statusCode"] == 201
        assert _parse_body(res)["tenantId"] == "tenant-test"

    def test_put_item_called_with_correct_tenant_id(self):
        _mock_tenant_table.put_item.return_value = {}
        event = _event("POST", "/tenants", body={"name": "Acme"}, tenant_id="tenant-acme")
        ah.handler(event, None)
        item = _mock_tenant_table.put_item.call_args.kwargs["Item"]
        assert item["tenantId"] == "tenant-acme"
        assert item["name"] == "Acme"

    def test_defaults_name_and_plan(self):
        _mock_tenant_table.put_item.return_value = {}
        event = _event("POST", "/tenants", body={})
        ah.handler(event, None)
        item = _mock_tenant_table.put_item.call_args.kwargs["Item"]
        assert item["name"] == "Unnamed Tenant"
        assert item["plan"] == "free"


# ── POST /ingest ───────────────────────────────────────────────────────────────

class TestIngest:
    def setup_method(self):
        ah.kinesis = _mock_kinesis
        _mock_kinesis.put_record.reset_mock()

    def test_puts_record_on_kinesis(self):
        event = _event("POST", "/ingest", body={"cpu_util": 0.5})
        res = ah.handler(event, None)
        assert res["statusCode"] == 202
        _mock_kinesis.put_record.assert_called_once()

    def test_partition_key_is_tenant_id(self):
        event = _event("POST", "/ingest", body={"cpu_util": 0.5}, tenant_id="tenant-x")
        ah.handler(event, None)
        kwargs = _mock_kinesis.put_record.call_args.kwargs
        assert kwargs["PartitionKey"] == "tenant-x"

    def test_tenant_id_injected_into_record(self):
        event = _event("POST", "/ingest", body={"cpu_util": 0.5}, tenant_id="tenant-y")
        ah.handler(event, None)
        kwargs = _mock_kinesis.put_record.call_args.kwargs
        record = json.loads(kwargs["Data"].decode())
        assert record["tenantId"] == "tenant-y"
        assert record["cpu_util"] == 0.5


# ── GET /admin/tenants ─────────────────────────────────────────────────────────

class TestAdminListTenants:
    def test_non_admin_gets_403(self):
        event = _event("GET", "/admin/tenants")  # no admin groups
        res = ah.handler(event, None)
        assert res["statusCode"] == 403

    def test_admin_gets_tenant_list(self):
        _mock_tenant_table.scan.return_value = {
            "Items": [
                {"tenantId": "t1", "sk": "CONFIG", "createdAt": "2026-01-01T00:00:00Z"},
                {"tenantId": "t2", "sk": "CONFIG", "createdAt": "2026-01-02T00:00:00Z"},
            ]
        }
        event = _admin_event("GET", "/admin/tenants")
        res = ah.handler(event, None)
        assert res["statusCode"] == 200
        body = _parse_body(res)
        assert len(body["tenants"]) == 2


# ── POST /admin/tenants ────────────────────────────────────────────────────────

class TestAdminCreateTenant:
    def setup_method(self):
        ah.cognito = _mock_cognito
        _mock_cognito.admin_create_user.reset_mock()
        _mock_cognito.admin_set_user_password.reset_mock()
        _mock_tenant_table.put_item.reset_mock()

    def test_non_admin_gets_403(self):
        event = _event("POST", "/admin/tenants",
                       body={"email": "x@y.com", "password": "Test1234!"})
        res = ah.handler(event, None)
        assert res["statusCode"] == 403

    def test_missing_email_returns_400(self):
        event = _admin_event("POST", "/admin/tenants",
                             body={"password": "Test1234!"})
        res = ah.handler(event, None)
        assert res["statusCode"] == 400

    def test_missing_password_returns_400(self):
        event = _admin_event("POST", "/admin/tenants",
                             body={"email": "user@example.com"})
        res = ah.handler(event, None)
        assert res["statusCode"] == 400

    def test_creates_cognito_user_and_sets_password(self):
        _mock_cognito.admin_create_user.return_value = {}
        _mock_cognito.admin_set_user_password.return_value = {}
        _mock_tenant_table.put_item.return_value = {}
        event = _admin_event("POST", "/admin/tenants",
                             body={"email": "new@corp.com", "name": "Corp", "password": "Pass1234!"})
        res = ah.handler(event, None)
        assert res["statusCode"] == 201
        _mock_cognito.admin_create_user.assert_called_once()
        _mock_cognito.admin_set_user_password.assert_called_once()

    def test_tenant_id_derived_from_email(self):
        _mock_cognito.admin_create_user.return_value = {}
        _mock_cognito.admin_set_user_password.return_value = {}
        _mock_tenant_table.put_item.return_value = {}
        event = _admin_event("POST", "/admin/tenants",
                             body={"email": "alice.smith@example.com",
                                   "name": "Alice", "password": "Pass1234!"})
        res = ah.handler(event, None)
        body = _parse_body(res)
        assert body["tenantId"] == "tenant-alice-smith"

    def test_tenant_record_persisted(self):
        _mock_cognito.admin_create_user.return_value = {}
        _mock_cognito.admin_set_user_password.return_value = {}
        _mock_tenant_table.put_item.return_value = {}
        event = _admin_event("POST", "/admin/tenants",
                             body={"email": "bob@corp.com", "name": "Bob Corp",
                                   "plan": "pro", "password": "Pass1234!"})
        ah.handler(event, None)
        item = _mock_tenant_table.put_item.call_args.kwargs["Item"]
        assert item["name"] == "Bob Corp"
        assert item["plan"] == "pro"
        assert item["email"] == "bob@corp.com"


# ── GET /admin/alerts ──────────────────────────────────────────────────────────

class TestAdminListAlerts:
    def test_non_admin_gets_403(self):
        event = _event("GET", "/admin/alerts")
        res = ah.handler(event, None)
        assert res["statusCode"] == 403

    def test_admin_gets_all_alerts(self):
        _mock_alert_table.scan.return_value = {
            "Items": [
                {"alertId": "a1", "tenantId": "t1", "createdAt": "2026-01-02T00:00:00Z"},
                {"alertId": "a2", "tenantId": "t2", "createdAt": "2026-01-01T00:00:00Z"},
            ]
        }
        event = _admin_event("GET", "/admin/alerts")
        res = ah.handler(event, None)
        assert res["statusCode"] == 200
        body = _parse_body(res)
        assert len(body["alerts"]) == 2
        # Should be sorted newest-first
        assert body["alerts"][0]["alertId"] == "a1"
