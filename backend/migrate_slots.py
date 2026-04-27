"""
Jednorazowa migracja slots_json — zmiana starych nazw pól na nowe.
Uruchom: python migrate_slots.py
"""
import sqlite3
import json

DB_PATH = "lab.db"

# Przemianowania top-level
RENAME_TOP = {
    "title": "heading",
    "subtitle": "body",
    "cta_primary": "cta",
    "cta_secondary": "cta2",
    "cta_secondary_text": "cta2",
    "cta_text": "cta",
    "pre_title": "eyebrow",
    "logo_text": "logo",
    "menu_items": "links",
    "solutions": "features",
    "benefits": "points",
    "services": "tiers",
    "plans": "tiers",
    "steps": "features",
    "highlights": "points",
    "members": "points",
    "columns": "cols",
}


def migrate(code: str, slots: dict) -> dict:
    # Top-level renames
    for old, new in RENAME_TOP.items():
        if old in slots:
            if old == "title" and code == "LO1":
                continue  # LO1 czyta f.title — zostawiamy
            if new not in slots:
                slots[new] = slots.pop(old)
            else:
                slots.pop(old)

    # FO1: description → desc
    if code == "FO1":
        if "description" in slots and "desc" not in slots:
            slots["desc"] = slots.pop("description")
    else:
        # Pozostałe: description → body
        if "description" in slots and "body" not in slots:
            slots["body"] = slots.pop("description")

    # links: [{label, url}] → ["label", ...]
    if "links" in slots and isinstance(slots["links"], list):
        slots["links"] = [
            item.get("label") or item.get("text") or str(item)
            if isinstance(item, dict) else str(item)
            for item in slots["links"]
        ]

    # features items: description → body
    if "features" in slots and isinstance(slots["features"], list):
        for item in slots["features"]:
            if isinstance(item, dict) and "description" in item and "body" not in item:
                item["body"] = item.pop("description")

    # tiers items: title → name, description → desc
    if "tiers" in slots and isinstance(slots["tiers"], list):
        for item in slots["tiers"]:
            if isinstance(item, dict):
                if "title" in item and "name" not in item:
                    item["name"] = item.pop("title")
                if "description" in item and "desc" not in item:
                    item["desc"] = item.pop("description")

    # points: [{title/text/name, description}] → ["tekst", ...]
    if "points" in slots and isinstance(slots["points"], list):
        new_points = []
        for item in slots["points"]:
            if isinstance(item, dict):
                text = (item.get("title") or item.get("text") or
                        item.get("name") or item.get("label") or "")
                desc = item.get("description") or item.get("body") or ""
                if desc:
                    text = f"{text} — {desc}" if text else desc
                new_points.append(text)
            else:
                new_points.append(str(item))
        slots["points"] = new_points

    return slots


def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, block_code, slots_json FROM project_sections")
    rows = c.fetchall()

    updated = 0
    for row_id, block_code, slots_raw in rows:
        if not slots_raw:
            continue
        slots = json.loads(slots_raw)
        new_slots = migrate(block_code or "", slots)
        c.execute(
            "UPDATE project_sections SET slots_json = ? WHERE id = ?",
            (json.dumps(new_slots, ensure_ascii=False), row_id)
        )
        updated += 1

    conn.commit()
    conn.close()
    print(f"Zaktualizowano {updated} sekcji.")


if __name__ == "__main__":
    main()
