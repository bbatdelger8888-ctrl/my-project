import pytest

from scoring import (
    WEIGHTS, degree_score, projects_score, software_score, total_score, years_score,
)


def test_weights_sum_to_100():
    assert sum(WEIGHTS.values()) == 100


@pytest.mark.parametrize("years,expected", [(0, 0), (5, 2.5), (10, 5), (20, 10), (35, 10), (-3, 0)])
def test_years(years, expected):
    assert years_score(years) == pytest.approx(expected)


def test_degree_max_is_weight():
    assert degree_score("doctor", "consulting") == WEIGHTS["degree"]
    assert degree_score("master", "certified") == 6.5
    assert degree_score("none", "none") == 0


def test_projects():
    # том × төвөгтэй = 9, дунд × дунд = 4 → 13 / 30 * 40
    projects = [
        {"size": "large", "complexity": "complex"},
        {"size": "medium", "complexity": "moderate"},
    ]
    assert projects_score(projects) == pytest.approx(13 / 30 * 40)
    assert projects_score([{"size": "large", "complexity": "complex"}] * 10) == 40


def test_software_dedup_and_cap():
    skills = [
        {"name": "Surpac", "level": "beginner"},
        {"name": "Surpac", "level": "advanced"},
        {"name": "Excel", "level": "intermediate"},
    ]
    assert software_score(skills) == pytest.approx(5 / 15 * 40)
    many = [{"name": f"S{i}", "level": "advanced"} for i in range(10)]
    assert software_score(many) == 40


def test_total_max_is_100():
    eng = {"years": 25, "academic": "doctor", "professional": "consulting"}
    projects = [{"size": "large", "complexity": "complex"}] * 4
    skills = [{"name": f"S{i}", "level": "advanced"} for i in range(5)]
    assert total_score(eng, projects, skills)["total"] == 100
