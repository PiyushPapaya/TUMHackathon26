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
