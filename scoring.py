"""Инженерийн онооны томьёо / Engineer scoring formula.

Нийт 100 оноо:
  - Ажилласан жил       10
  - Зэрэг               10 (эрдмийн 5 + мэргэжлийн 5)
  - Хийсэн төсөл        40
  - Программ хангамж    40
"""

WEIGHTS = {"years": 10, "degree": 10, "projects": 40, "software": 40}

YEARS_CAP = 20  # 20+ жил ажилласан бол бүтэн оноо

ACADEMIC_POINTS = {"none": 0, "bachelor": 2, "master": 3.5, "doctor": 5}
PROFESSIONAL_POINTS = {"none": 0, "certified": 3, "consulting": 5}

# Хэмжээ: жижиг 1, дунд 2, том 3. Төвөгшил: энгийн 1, дунд 2, төвөгтэй 3.
PROJECT_SIZES = {"small": 1, "medium": 2, "large": 3}
PROJECT_COMPLEXITIES = {"simple": 1, "moderate": 2, "complex": 3}
PROJECTS_CAP = 30  # төслийн түүхий онооны дээд хязгаар

SOFTWARE_LIST = [
    "Surpac", "Datamine", "Micromine", "Vulcan", "Deswik", "Leapfrog",
    "AutoCAD", "Whittle", "ArcGIS", "Excel", "Word",
]
SOFTWARE_LEVELS = {"beginner": 1, "intermediate": 2, "advanced": 3}
SOFTWARE_CAP = 15  # программын түүхий онооны дээд хязгаар


def years_score(years):
    years = max(0.0, float(years or 0))
    return min(years, YEARS_CAP) / YEARS_CAP * WEIGHTS["years"]


def degree_score(academic, professional):
    return ACADEMIC_POINTS.get(academic, 0) + PROFESSIONAL_POINTS.get(professional, 0)


def projects_score(projects):
    raw = sum(
        PROJECT_SIZES.get(p["size"], 0) * PROJECT_COMPLEXITIES.get(p["complexity"], 0)
        for p in projects
    )
    return min(raw, PROJECTS_CAP) / PROJECTS_CAP * WEIGHTS["projects"]


def software_score(skills):
    # Нэг программыг давхар тоолохгүй: хамгийн өндөр түвшнийг авна.
    best = {}
    for s in skills:
        level = SOFTWARE_LEVELS.get(s["level"], 0)
        best[s["name"]] = max(best.get(s["name"], 0), level)
    raw = sum(best.values())
    return min(raw, SOFTWARE_CAP) / SOFTWARE_CAP * WEIGHTS["software"]


def total_score(engineer, projects, skills):
    parts = {
        "years": years_score(engineer["years"]),
        "degree": degree_score(engineer["academic"], engineer["professional"]),
        "projects": projects_score(projects),
        "software": software_score(skills),
    }
    parts["total"] = sum(parts.values())
    return {k: round(v, 1) for k, v in parts.items()}
