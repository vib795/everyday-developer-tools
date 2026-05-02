def test_cron_next_5(client):
    r = client.post(
        "/api/calc/cron-next",
        json={"expression": "0 9 * * 1-5", "count": 5, "timezone": "UTC"},
    )
    body = r.json()
    assert body["error"] is None
    assert len(body["runs"]) == 5


def test_cron_invalid(client):
    r = client.post(
        "/api/calc/cron-next",
        json={"expression": "not a cron", "count": 3},
    )
    assert r.json()["error"] is not None


def test_cron_with_timezone(client):
    r = client.post(
        "/api/calc/cron-next",
        json={"expression": "0 0 * * *", "count": 2, "timezone": "America/New_York"},
    )
    runs = r.json()["runs"]
    assert len(runs) == 2
    # Just check ISO timestamps come back
    assert all("T" in run for run in runs)


def test_color_hex(client):
    r = client.post("/api/calc/color", json={"color": "#ff0080"})
    body = r.json()
    assert body["hex"] == "#ff0080"
    assert "rgb(255, 0, 128)" == body["rgb"]
    assert body["hsl"].startswith("hsl(")
    assert body["oklch"].startswith("oklch(")


def test_color_short_hex(client):
    r = client.post("/api/calc/color", json={"color": "#abc"})
    assert r.json()["hex"] == "#aabbcc"


def test_color_rgb_input(client):
    r = client.post("/api/calc/color", json={"color": "rgb(255,0,0)"})
    assert r.json()["hex"] == "#ff0000"


def test_color_hsl_input(client):
    r = client.post("/api/calc/color", json={"color": "hsl(0, 100%, 50%)"})
    assert r.json()["hex"] == "#ff0000"


def test_color_invalid(client):
    r = client.post("/api/calc/color", json={"color": "purple"})
    assert r.json()["error"]


def test_contrast_black_on_white(client):
    r = client.post(
        "/api/calc/contrast",
        json={"foreground": "#000000", "background": "#ffffff"},
    )
    body = r.json()
    assert body["ratio"] == 21.0
    assert body["aa_normal"] is True
    assert body["aaa_normal"] is True


def test_contrast_low(client):
    r = client.post(
        "/api/calc/contrast",
        json={"foreground": "#888888", "background": "#999999"},
    )
    body = r.json()
    assert body["aa_normal"] is False


def test_chmod_numeric_to_symbolic(client):
    r = client.post("/api/calc/chmod", json={"value": "755"})
    body = r.json()
    assert body["numeric"] == "0755"
    assert body["symbolic"] == "rwxr-xr-x"


def test_chmod_symbolic_to_numeric(client):
    r = client.post("/api/calc/chmod", json={"value": "rwxr-xr-x"})
    body = r.json()
    assert body["numeric"] == "0755"


def test_chmod_setuid(client):
    r = client.post("/api/calc/chmod", json={"value": "4755"})
    body = r.json()
    assert body["symbolic"] == "rwsr-xr-x"


def test_chmod_sticky(client):
    r = client.post("/api/calc/chmod", json={"value": "1777"})
    body = r.json()
    assert body["symbolic"] == "rwxrwxrwt"


def test_chmod_invalid(client):
    r = client.post("/api/calc/chmod", json={"value": "abc"})
    assert r.json()["error"]


def test_cidr_v4(client):
    r = client.post("/api/calc/cidr", json={"cidr": "10.0.0.0/24"})
    body = r.json()
    assert body["network"] == "10.0.0.0"
    assert body["netmask"] == "255.255.255.0"
    assert body["broadcast"] == "10.0.0.255"
    assert body["first_host"] == "10.0.0.1"
    assert body["last_host"] == "10.0.0.254"
    assert body["num_hosts"] == 254
    assert body["prefix"] == 24
    assert body["version"] == 4


def test_cidr_v6(client):
    r = client.post("/api/calc/cidr", json={"cidr": "2001:db8::/64"})
    body = r.json()
    assert body["version"] == 6
    assert body["prefix"] == 64
    assert body["broadcast"] is None


def test_cidr_host_inside_network(client):
    # strict=False should accept addresses with host bits set
    r = client.post("/api/calc/cidr", json={"cidr": "10.0.0.5/24"})
    body = r.json()
    assert body["network"] == "10.0.0.0"


def test_cidr_invalid(client):
    r = client.post("/api/calc/cidr", json={"cidr": "not an ip"})
    assert r.json()["error"]


def test_markdown_preview(client):
    r = client.post(
        "/api/calc/markdown",
        json={"text": "# title\n\n- a\n- b\n\n```py\nx=1\n```\n"},
    )
    html = r.json()["html"]
    assert "<h1>" in html and "title" in html
    assert "<ul>" in html and "<li>a</li>" in html
    assert "<code" in html and "x=1" in html
