def test_md_to_pdf(client):
    md = "# Title\n\n- one\n- two\n\nSome paragraph.\n\n```py\nprint('hi')\n```\n"
    r = client.post("/api/document/md-to-pdf", json={"markdown_text": md})
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content.startswith(b"%PDF")
    assert "attachment" in r.headers["content-disposition"]


def test_md_to_pdf_validation(client):
    r = client.post("/api/document/md-to-pdf", json={"markdown_text": 123})
    assert r.status_code == 400


def test_pdf_to_md(client):
    # First produce a real PDF with the md->pdf endpoint, then round-trip it.
    md = "# Hello"
    pdf = client.post("/api/document/md-to-pdf", json={"markdown_text": md}).content
    r = client.post(
        "/api/document/pdf-to-md",
        files={"pdf_file": ("doc.pdf", pdf, "application/pdf")},
    )
    assert r.status_code == 200
    assert "Hello" in r.json()["text"]
