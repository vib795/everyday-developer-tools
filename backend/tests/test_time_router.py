def test_iso_input(client):
    r = client.post("/api/time/convert", json={"time_input": "2024-01-01T12:00:00+00:00"})
    assert r.status_code == 200
    out = r.json()["output"]
    assert "UTC Time" in out
    assert out["Day of week"] == "Monday"
    assert out["Is leap year?"] == "Yes"


def test_epoch_seconds(client):
    r = client.post("/api/time/convert", json={"time_input": "1700000000"})
    assert r.status_code == 200
    assert "UTC Time" in r.json()["output"]


def test_epoch_milliseconds(client):
    r = client.post("/api/time/convert", json={"time_input": "1700000000000"})
    assert r.status_code == 200
    assert "UTC Time" in r.json()["output"]


def test_postgres_timestamp(client):
    r = client.post(
        "/api/time/convert", json={"time_input": "2024-06-01 09:30:00"}
    )
    assert r.status_code == 200
    assert "ISO Format" in r.json()["output"]


def test_invalid_time(client):
    r = client.post("/api/time/convert", json={"time_input": "totally-not-time"})
    assert r.status_code == 400


def test_cron(client):
    r = client.post(
        "/api/time/cron",
        json={
            "minute": "0",
            "hour": "5",
            "day_of_month": "*",
            "month": "*",
            "day_of_week": "*",
        },
    )
    assert r.json()["expression"] == "0 5 * * *"
