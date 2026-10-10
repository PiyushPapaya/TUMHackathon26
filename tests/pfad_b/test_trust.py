"""B2: Vertrauen allein aus der Domain. Keine Netzaufrufe."""

import pytest

from evidence_external.trust import trust_for_url


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://www.caranddriver.com/reviews/2025-mercedes-benz-e-class", "high"),  # Testmagazin
        ("https://www.jdpower.com/cars/ratings", "high"),  # Studie/Institut
        ("https://www.mbusa.com/en/vehicles/class/e-class", "high"),  # Hersteller (US-Seite)
        ("https://www.insideevs.com/news/audi-a6-etron", "medium"),  # Fachpresse
        ("https://www.reddit.com/r/BMW/comments/abc", "low"),  # Forum/Social
        ("https://m.youtube.com/watch?v=xyz", "low"),  # Subdomain von youtube
        ("https://notcaranddriver.com/fake", "low"),  # nur exakte Domain/Subdomain, kein Teilstring
        ("kein-url", "low"),  # kaputte URL
    ],
)
def test_vertrauen_nach_domain(url, expected):
    assert trust_for_url(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "https://evil.com\\@caranddriver.com/x",  # Browser ruft evil.com auf, urlparse sieht caranddriver.com
        "https://caranddriver.com@evil.com/",  # Userinfo: echter Host ist evil.com
        "https://caranddriver.com\t.evil.com/",  # Steuerzeichen werden vom Browser entfernt
        "javascript://caranddriver.com/%0aalert(1)",  # kein Web-Schema
        "ftp://caranddriver.com/x",
        "//caranddriver.com/x",  # ohne Schema
    ],
)
def test_url_tricks_sind_nie_vertrauenswuerdig(url):
    assert trust_for_url(url) == "low"
