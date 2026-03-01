"""
Domyślne role i uprawnienia FastHub.
Tworzone automatycznie przy pierwszym uruchomieniu lub przy tworzeniu nowej organizacji.

Aplikacje (AutoFlow, CRM) ROZSZERZAJĄ te uprawnienia o swoje —
nie zmieniają istniejących.
"""

# === UPRAWNIENIA BAZOWE FastHub ===
# Format: "kategoria.akcja"

CORE_PERMISSIONS = {
    "team": [
        ("team.view_members", "Podgląd listy członków organizacji"),
        ("team.invite_member", "Zapraszanie nowych członków"),
        ("team.remove_member", "Usuwanie członków z organizacji"),
        ("team.change_roles", "Zmiana ról członków"),
    ],
    "billing": [
        ("billing.view_plans", "Podgląd dostępnych planów"),
        ("billing.change_plan", "Zmiana planu subskrypcji"),
        ("billing.view_invoices", "Podgląd faktur"),
        ("billing.manage_addons", "Zarządzanie dodatkami do planu"),
    ],
    "settings": [
        ("settings.view", "Podgląd ustawień organizacji"),
        ("settings.edit", "Edycja ustawień organizacji"),
        ("settings.manage_integrations", "Zarządzanie integracjami"),
    ],
    "audit": [
        ("audit.view_log", "Podgląd logów aktywności"),
        ("audit.export_log", "Eksport logów do CSV/PDF"),
    ],
}

# === ROLE SYSTEMOWE ===
# Tworzone dla KAŻDEJ nowej organizacji

SYSTEM_ROLES = {
    "owner": {
        "name": "Owner",
        "description": "Właściciel organizacji — pełne uprawnienia",
        "is_system": True,
        "is_default": False,
        "permissions": "*",  # WSZYSTKIE uprawnienia
    },
    "admin": {
        "name": "Admin",
        "description": "Administrator — zarządza zespołem i ustawieniami",
        "is_system": True,
        "is_default": False,
        "permissions": [
            "team.view_members", "team.invite_member", "team.remove_member", "team.change_roles",
            "billing.view_plans", "billing.view_invoices",
            "settings.view", "settings.edit", "settings.manage_integrations",
            "audit.view_log",
        ],
    },
    "member": {
        "name": "Member",
        "description": "Zwykły członek — podstawowe uprawnienia",
        "is_system": True,
        "is_default": True,  # Nowi członkowie dostają tę rolę
        "permissions": [
            "team.view_members",
            "billing.view_plans",
            "settings.view",
        ],
    },
}


def get_all_core_permission_names() -> list:
    """Zwraca flat listę nazw wszystkich bazowych uprawnień"""
    result = []
    for category, perms in CORE_PERMISSIONS.items():
        for name, description in perms:
            result.append(name)
    return result
