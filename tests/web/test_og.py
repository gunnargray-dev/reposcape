from src.web.og import parse_repo_ref, share_card_url


def test_parse_repo_ref_valid() -> None:
    ref = parse_repo_ref("owner/repo")
    assert ref.owner == "owner"
    assert ref.name == "repo"
    assert ref.slug == "owner/repo"


def test_parse_repo_ref_invalid() -> None:
    for raw in ["", "owner", "owner/", "/repo", "owner/repo/extra", "owner repo"]:
        try:
            parse_repo_ref(raw)
            raise AssertionError(f"Expected ValueError for {raw!r}")
        except ValueError:
            pass


def test_share_card_url_encodes() -> None:
    url = share_card_url(
        base_url="https://example.com/",
        title="a/b",
        subtitle="hello world",
    )
    assert url.startswith("https://example.com/share/card.png?")
    assert "title=a/b" not in url
    assert "subtitle=hello world" not in url
    assert "subtitle=hello%20world" in url
