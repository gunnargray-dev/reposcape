from src.web.app import create_app


def test_story_route_renders_og_tags() -> None:
    app = create_app()

    # Call handler directly to avoid adding extra test dependencies (httpx).
    route = next(r for r in app.router.routes if getattr(r, "path", None) == "/r/{owner}/{repo}")
    endpoint = route.endpoint

    class _Req:  # minimal stand-in for FastAPI Request
        def __init__(self, base_url: str):
            self.base_url = base_url

    resp = endpoint(_Req("https://example.com/"), owner="gunnargray-dev", repo="reposcape")
    html = resp.body.decode()

    assert "og:image" in html
    assert "twitter:card" in html
    assert "/share/card.png?" in html
    assert "gunnargray-dev/reposcape" in html
