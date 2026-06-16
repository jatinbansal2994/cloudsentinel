"""
Unit tests for ml/inference/serve.py.
Uses real numpy arrays and a mock sklearn model — no SageMaker needed.
"""
import sys
import json
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

ML_DIR = str(Path(__file__).parent.parent / "ml" / "inference")
sys.path.insert(0, ML_DIR)

import serve  # noqa: E402


# ── Fixtures ───────────────────────────────────────────────────────────────────

def _mock_artifacts(predictions, scores):
    """Return a model_artifacts dict with predictable outputs."""
    model = MagicMock()
    scaler = MagicMock()
    # scaler.transform just passes the data through
    scaler.transform.side_effect = lambda X: X
    model.predict.return_value = np.array(predictions)
    model.decision_function.return_value = np.array(scores)
    return {"model": model, "scaler": scaler}


NORMAL_RECORD = {
    "cpu_util": 0.1, "memory_util": 0.3,
    "latency_ms": 50.0, "error_rate": 0.01, "request_count": 200.0,
}

ANOMALY_RECORD = {
    "cpu_util": 0.99, "memory_util": 0.95,
    "latency_ms": 5000.0, "error_rate": 0.8, "request_count": 5.0,
}


# ── input_fn() ─────────────────────────────────────────────────────────────────

class TestInputFn:
    def test_single_dict_parsed_to_2d_array(self):
        X = serve.input_fn(json.dumps(NORMAL_RECORD))
        assert X.shape == (1, 5)
        assert X.dtype == np.float64

    def test_list_of_dicts_parsed_correctly(self):
        X = serve.input_fn(json.dumps([NORMAL_RECORD, ANOMALY_RECORD]))
        assert X.shape == (2, 5)

    def test_feature_order_matches_FEATURES_constant(self):
        record = {f: float(i) for i, f in enumerate(serve.FEATURES)}
        X = serve.input_fn(json.dumps(record))
        expected = np.array([[float(i) for i in range(5)]])
        np.testing.assert_array_equal(X, expected)

    def test_missing_features_default_to_zero(self):
        X = serve.input_fn(json.dumps({}))
        np.testing.assert_array_equal(X, np.zeros((1, 5)))

    def test_bytes_input_decoded_correctly(self):
        X = serve.input_fn(json.dumps(NORMAL_RECORD).encode("utf-8"))
        assert X.shape == (1, 5)

    def test_unsupported_content_type_raises(self):
        with pytest.raises(ValueError, match="Unsupported content type"):
            serve.input_fn("{}", content_type="text/plain")


# ── predict_fn() ───────────────────────────────────────────────────────────────

class TestPredictFn:
    def test_normal_prediction_returned(self):
        artifacts = _mock_artifacts([1], [0.07])
        X = np.array([[0.1, 0.3, 50.0, 0.01, 200.0]])
        result = serve.predict_fn(X, artifacts)
        assert result["predictions"] == [1]
        assert abs(result["scores"][0] - 0.07) < 1e-9

    def test_anomaly_prediction_returned(self):
        artifacts = _mock_artifacts([-1], [-0.45])
        X = np.array([[0.99, 0.95, 5000.0, 0.8, 5.0]])
        result = serve.predict_fn(X, artifacts)
        assert result["predictions"] == [-1]
        assert result["scores"][0] == pytest.approx(-0.45)

    def test_batch_results_length_matches_input(self):
        artifacts = _mock_artifacts([1, -1, 1], [0.05, -0.3, 0.08])
        X = np.zeros((3, 5))
        result = serve.predict_fn(X, artifacts)
        assert len(result["predictions"]) == 3
        assert len(result["scores"]) == 3

    def test_scores_rounded_to_6_decimal_places(self):
        artifacts = _mock_artifacts([1], [0.1234567890])
        X = np.zeros((1, 5))
        result = serve.predict_fn(X, artifacts)
        assert result["scores"][0] == round(0.1234567890, 6)

    def test_scaler_is_applied_before_model(self):
        artifacts = _mock_artifacts([1], [0.05])
        X = np.array([[1.0, 2.0, 3.0, 4.0, 5.0]])
        serve.predict_fn(X, artifacts)
        # scaler.transform(X) is called; its output is passed to model.predict
        artifacts["scaler"].transform.assert_called_once_with(X)
        artifacts["model"].predict.assert_called_once()


# ── output_fn() ────────────────────────────────────────────────────────────────

class TestOutputFn:
    def test_returns_json_string_and_content_type(self):
        payload = {"predictions": [1], "scores": [0.07]}
        body, ct = serve.output_fn(payload)
        assert ct == "application/json"
        assert json.loads(body) == payload

    def test_unsupported_accept_raises(self):
        with pytest.raises(ValueError, match="Unsupported accept type"):
            serve.output_fn({}, accept="text/plain")

    def test_empty_predictions_serialised(self):
        payload = {"predictions": [], "scores": []}
        body, _ = serve.output_fn(payload)
        assert json.loads(body) == {"predictions": [], "scores": []}


# ── round-trip: input → predict → output ──────────────────────────────────────

class TestRoundTrip:
    def test_normal_record_round_trip(self):
        artifacts = _mock_artifacts([1], [0.08])
        X = serve.input_fn(json.dumps(NORMAL_RECORD))
        prediction = serve.predict_fn(X, artifacts)
        body, ct = serve.output_fn(prediction)
        result = json.loads(body)
        assert result["predictions"] == [1]
        assert result["scores"] == [0.08]
        assert ct == "application/json"

    def test_anomaly_record_round_trip(self):
        artifacts = _mock_artifacts([-1], [-0.42])
        X = serve.input_fn(json.dumps(ANOMALY_RECORD))
        prediction = serve.predict_fn(X, artifacts)
        body, _ = serve.output_fn(prediction)
        result = json.loads(body)
        assert result["predictions"] == [-1]
        assert result["scores"][0] == pytest.approx(-0.42)
