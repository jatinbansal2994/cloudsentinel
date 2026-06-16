"""
Unit tests for lambda/stream-processor/index.py.
Mocks all boto3 calls so no AWS credentials are needed.
"""
import sys
import os
import json
import base64
from pathlib import Path
from unittest.mock import MagicMock, patch, call

# Set required env vars before the module loads
os.environ.setdefault("ALERT_TABLE", "test-alerts")
os.environ.setdefault("SAGEMAKER_ENDPOINT", "test-endpoint")
os.environ.setdefault("ALERT_TOPIC_ARN", "arn:aws:sns:us-east-1:123456789012:test-alerts")

import importlib.util

PROC_INDEX = Path(__file__).parent.parent / "lambda" / "stream-processor" / "index.py"

# Patch boto3 before the module-level resource/client calls execute.
# Use a unique module name to avoid colliding with the api-handler's index.py.
_mock_ddb = MagicMock()
_mock_table = MagicMock()
_mock_ddb.Table.return_value = _mock_table
_mock_sm = MagicMock()
_mock_sns = MagicMock()

def _client_factory(service_name, **kwargs):
    if service_name == "sagemaker-runtime":
        return _mock_sm
    if service_name == "sns":
        return _mock_sns
    return MagicMock()

with patch("boto3.resource", return_value=_mock_ddb), \
     patch("boto3.client", side_effect=_client_factory):
    _spec = importlib.util.spec_from_file_location("stream_processor_index", PROC_INDEX)
    sp = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(sp)


# ── helpers ────────────────────────────────────────────────────────────────────

def _kinesis_event(*payloads) -> dict:
    """Wrap dicts as a Kinesis event the handler understands."""
    records = []
    for p in payloads:
        raw = json.dumps(p).encode()
        records.append({"kinesis": {"data": base64.b64encode(raw).decode()}})
    return {"Records": records}


def _sm_response(prediction: int, score: float) -> MagicMock:
    body = MagicMock()
    body.read.return_value = json.dumps(
        {"predictions": [prediction], "scores": [score]}
    ).encode()
    return {"Body": body}


# ── severity() ─────────────────────────────────────────────────────────────────

class TestSeverity:
    def test_critical(self):
        assert sp.severity(-0.05) == "critical"

    def test_high(self):
        assert sp.severity(-0.02) == "high"

    def test_medium(self):
        assert sp.severity(0.01) == "medium"

    def test_low(self):
        assert sp.severity(0.10) == "low"

    def test_boundary_critical_high(self):
        # -0.04 is NOT < -0.04, so falls through to high
        assert sp.severity(-0.04) == "high"

    def test_boundary_high_medium(self):
        assert sp.severity(-0.01) == "medium"

    def test_boundary_medium_low(self):
        assert sp.severity(0.03) == "low"

    def test_exactly_zero(self):
        assert sp.severity(0.0) == "medium"


# ── handler() ─────────────────────────────────────────────────────────────────

class TestHandler:
    def test_empty_records(self):
        result = sp.handler({"Records": []}, None)
        assert result["processed"] == 0
        assert result["alerts"] == 0

    def test_missing_tenant_id_skipped(self):
        event = _kinesis_event({"cpu_util": 0.5})
        with patch.object(sp, "invoke_sagemaker", return_value=(1, 0.1)):
            result = sp.handler(event, None)
        assert result["processed"] == 1
        assert result["alerts"] == 0

    def test_normal_prediction_no_alert(self):
        event = _kinesis_event({"tenantId": "t1", "cpu_util": 0.1})
        with patch.object(sp, "invoke_sagemaker", return_value=(1, 0.1)), \
             patch.object(sp, "write_alert") as mock_write, \
             patch.object(sp, "publish_sns") as mock_pub:
            result = sp.handler(event, None)
        assert result["alerts"] == 0
        mock_write.assert_not_called()
        mock_pub.assert_not_called()

    def test_anomaly_prediction_writes_alert_and_publishes(self):
        event = _kinesis_event({"tenantId": "t1", "cpu_util": 0.99})
        with patch.object(sp, "invoke_sagemaker", return_value=(-1, -0.5)), \
             patch.object(sp, "write_alert", return_value="alert-123") as mock_write, \
             patch.object(sp, "publish_sns") as mock_pub:
            result = sp.handler(event, None)
        assert result["alerts"] == 1
        mock_write.assert_called_once()
        mock_pub.assert_called_once_with("t1", "alert-123", {"tenantId": "t1", "cpu_util": 0.99}, -0.5)

    def test_score_below_threshold_triggers_alert_even_if_prediction_normal(self):
        # prediction=1 (normal) but score < SCORE_THRESHOLD (0.03)
        event = _kinesis_event({"tenantId": "t1", "cpu_util": 0.5})
        with patch.object(sp, "invoke_sagemaker", return_value=(1, -0.05)), \
             patch.object(sp, "write_alert", return_value="alert-abc") as mock_write, \
             patch.object(sp, "publish_sns"):
            result = sp.handler(event, None)
        assert result["alerts"] == 1
        mock_write.assert_called_once()

    def test_multiple_records_processed(self):
        event = _kinesis_event(
            {"tenantId": "t1", "cpu_util": 0.1},
            {"tenantId": "t2", "cpu_util": 0.2},
        )
        with patch.object(sp, "invoke_sagemaker", return_value=(1, 0.1)), \
             patch.object(sp, "write_alert"), patch.object(sp, "publish_sns"):
            result = sp.handler(event, None)
        assert result["processed"] == 2
        assert result["alerts"] == 0

    def test_multiple_anomalies_all_counted(self):
        event = _kinesis_event(
            {"tenantId": "t1", "cpu_util": 0.99},
            {"tenantId": "t2", "cpu_util": 0.98},
        )
        with patch.object(sp, "invoke_sagemaker", return_value=(-1, -0.5)), \
             patch.object(sp, "write_alert", return_value="aid"), \
             patch.object(sp, "publish_sns"):
            result = sp.handler(event, None)
        assert result["alerts"] == 2


# ── invoke_sagemaker() ─────────────────────────────────────────────────────────

class TestInvokeSagemaker:
    def setup_method(self):
        # Reset to a clean mock before each test
        sp.sagemaker = MagicMock()

    def test_returns_correct_prediction_and_score(self):
        sp.sagemaker.invoke_endpoint.return_value = _sm_response(1, 0.07)
        pred, score = sp.invoke_sagemaker(
            {"cpu_util": 0.1, "memory_util": 0.3, "latency_ms": 50.0,
             "error_rate": 0.0, "request_count": 100}
        )
        assert pred == 1
        assert abs(score - 0.07) < 1e-9

    def test_anomaly_prediction_returned(self):
        sp.sagemaker.invoke_endpoint.return_value = _sm_response(-1, -0.45)
        pred, score = sp.invoke_sagemaker({"cpu_util": 0.99})
        assert pred == -1
        assert abs(score - (-0.45)) < 1e-9

    def test_missing_features_default_to_zero(self):
        sp.sagemaker.invoke_endpoint.return_value = _sm_response(1, 0.05)
        sp.invoke_sagemaker({})  # no features at all
        body_sent = sp.sagemaker.invoke_endpoint.call_args.kwargs["Body"]
        parsed = json.loads(body_sent)
        assert parsed == {
            "cpu_util": 0.0, "memory_util": 0.0, "latency_ms": 0.0,
            "error_rate": 0.0, "request_count": 0.0,
        }

    def test_sagemaker_error_returns_normal_treatment(self):
        sp.sagemaker.invoke_endpoint.side_effect = Exception("endpoint unreachable")
        pred, score = sp.invoke_sagemaker({"cpu_util": 0.99})
        assert pred == 1
        assert score == 0.0


# ── publish_sns() ──────────────────────────────────────────────────────────────

class TestPublishSns:
    def setup_method(self):
        sp.sns_client = MagicMock()

    def test_no_op_when_topic_arn_empty(self):
        original = sp.ALERT_TOPIC_ARN
        sp.ALERT_TOPIC_ARN = ""
        sp.publish_sns("t1", "aid-1", {}, -0.5)
        sp.sns_client.publish.assert_not_called()
        sp.ALERT_TOPIC_ARN = original

    def test_publishes_to_correct_topic(self):
        sp.ALERT_TOPIC_ARN = "arn:aws:sns:us-east-1:123:alerts"
        sp.publish_sns("t1", "aid-1", {"source": "test"}, -0.5)
        sp.sns_client.publish.assert_called_once()
        kwargs = sp.sns_client.publish.call_args.kwargs
        assert kwargs["TopicArn"] == "arn:aws:sns:us-east-1:123:alerts"

    def test_message_attributes_contain_tenant_and_severity(self):
        sp.ALERT_TOPIC_ARN = "arn:aws:sns:us-east-1:123:alerts"
        sp.publish_sns("tenant-abc", "aid-2", {}, -0.5)
        kwargs = sp.sns_client.publish.call_args.kwargs
        attrs = kwargs["MessageAttributes"]
        assert attrs["tenantId"]["StringValue"] == "tenant-abc"
        assert attrs["severity"]["StringValue"] == "critical"

    def test_sns_error_does_not_propagate(self):
        sp.ALERT_TOPIC_ARN = "arn:aws:sns:us-east-1:123:alerts"
        sp.sns_client.publish.side_effect = Exception("SNS down")
        sp.publish_sns("t1", "aid-3", {}, -0.5)  # must not raise
