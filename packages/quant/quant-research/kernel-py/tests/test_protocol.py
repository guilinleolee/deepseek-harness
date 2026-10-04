"""End-to-end protocol tests: spawn `python main.py`, write one request line, read one response."""

import json
import subprocess
import sys
from pathlib import Path

KERNEL = Path(__file__).resolve().parent.parent / "main.py"


def run_kernel(request: object) -> tuple:
    """Run one request through a real interpreter; return (code, stdout, stderr)."""
    proc = subprocess.run(
        [sys.executable, str(KERNEL)],
        input=json.dumps(request, ensure_ascii=False),
        capture_output=True,
        text=True,
        check=False,
        cwd=str(KERNEL.parent),
    )
    return proc.returncode, proc.stdout, proc.stderr


def test_ping_round_trip() -> None:
    code, stdout, stderr = run_kernel({"protocol": 1, "id": "p-1", "op": "ping", "params": {}})
    assert code == 0, stderr
    response = json.loads(stdout)
    assert response == {"id": "p-1", "ok": True, "result": {"protocol": 1, "python": response["result"]["python"]}}


def test_ping_rejects_wrong_protocol() -> None:
    code, stdout, _ = run_kernel({"protocol": 99, "id": "p-2", "op": "ping", "params": {}})
    assert code == 0
    response = json.loads(stdout)
    assert response["ok"] is False
    assert response["error"]["code"] == "BAD_REQUEST"


def test_unknown_op_fails_clean() -> None:
    code, stdout, _ = run_kernel({"protocol": 1, "id": "p-3", "op": "time_travel", "params": {}})
    assert code == 0
    response = json.loads(stdout)
    assert response["ok"] is False
    assert response["error"]["code"] == "BAD_REQUEST"


def test_get_kline_missing_param_fails_data_error() -> None:
    code, stdout, _ = run_kernel({"protocol": 1, "id": "p-4", "op": "get_kline", "params": {"source": "synthetic"}})
    assert code == 0
    response = json.loads(stdout)
    assert response["ok"] is False
    assert response["error"]["code"] == "BAD_REQUEST"


def test_get_kline_synthetic_round_trip() -> None:
    request = {
        "protocol": 1, "id": "p-5", "op": "get_kline",
        "params": {"source": "synthetic", "symbol": "000001", "period": "daily", "bars": 30},
    }
    code, stdout, stderr = run_kernel(request)
    assert code == 0, stderr
    response = json.loads(stdout)
    assert response["ok"] is True
    series = response["result"]
    assert len(series) == 30
    assert series[0]["date"] < series[-1]["date"]
    for bar in series:
        assert bar["high"] >= max(bar["open"], bar["close"])
        assert bar["low"] <= min(bar["open"], bar["close"])


def test_bad_json_exits_nonzero() -> None:
    proc = subprocess.run(
        [sys.executable, str(KERNEL)],
        input="not-json",
        capture_output=True,
        text=True,
        check=False,
        cwd=str(KERNEL.parent),
    )
    assert proc.returncode == 1
    assert proc.stdout == ""
    assert "JSON" in proc.stderr


def test_empty_input_exits_nonzero() -> None:
    proc = subprocess.run(
        [sys.executable, str(KERNEL)],
        input="",
        capture_output=True,
        text=True,
        check=False,
        cwd=str(KERNEL.parent),
    )
    assert proc.returncode == 1
