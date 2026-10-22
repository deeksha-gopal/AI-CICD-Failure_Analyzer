from app import config


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_and_history(client):
    response = client.post(
        "/api/analyze",
        data={"mode": "demo"},
        files={"file": ("failure.log", b"ModuleNotFoundError: No module named 'numpy'", "text/plain")},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["mode"] == "demo"
    assert data["findings"][0]["category"] == "dependencies"
    history = client.get("/api/history").json()
    assert len(history) == 1
    assert history[0]["id"] == data["id"]
    detail = client.get("/api/history/" + data["id"])
    assert detail.status_code == 200
    assert detail.json()["summary"] == data["summary"]


def test_redaction_applies_before_storage(client):
    content = b"password=very-secret-value\nAssertionError: 3 != 4"
    response = client.post("/api/analyze", files={"file": ("failure.log", content)})
    assert response.status_code == 201
    data = response.json()
    assert "very-secret-value" not in str(data)
    assert "[REDACTED]" in data["redacted_excerpt"]


def test_invalid_extension_and_empty_log(client):
    invalid = client.post("/api/analyze", files={"file": ("notes.exe", b"hello")})
    assert invalid.status_code == 400
    empty = client.post("/api/analyze", files={"file": ("a.log", b" ")})
    assert empty.status_code == 400


def test_oversize_log(client):
    response = client.post("/api/analyze", files={"file": ("huge.log", b"x" * (config.MAX_LOG_BYTES + 1))})
    assert response.status_code == 413


def test_llm_disabled_without_key(client, monkeypatch):
    monkeypatch.setattr(config, "OPENAI_API_KEY", "")
    response = client.post(
        "/api/analyze", data={"mode": "llm"},
        files={"file": ("failure.log", b"ERROR: missing module")},
    )
    assert response.status_code == 400
    assert "OPENAI_API_KEY" in response.json()["detail"]


def test_not_found(client):
    response = client.get("/api/history/does-not-exist")
    assert response.status_code == 404


def test_llm_mode_redacts_before_forwarding(client, monkeypatch):
    from app import main
    from app.schemas import AnalysisResult, Finding

    monkeypatch.setattr(config, "OPENAI_API_KEY", "test-only-key")
    captured = {}

    async def fake_llm(log: str) -> AnalysisResult:
        captured["log"] = log
        return AnalysisResult(
            summary="Mocked LLM result",
            findings=[Finding(
                category="testing", severity="low", title="Mock issue",
                evidence="AssertionError", explanation="Example test failure.",
                recommendations=["Re-run the test."],
            )],
            next_steps=["Check the assertion."],
        )

    monkeypatch.setattr(main, "analyze_with_llm", fake_llm)
    response = client.post(
        "/api/analyze", data={"mode": "llm"},
        files={"file": ("build.log", b"password=very-secret-value\nAssertionError")},
    )
    assert response.status_code == 201
    assert response.json()["mode"] == "llm"
    assert "very-secret-value" not in captured["log"]
    assert "[REDACTED]" in captured["log"]
