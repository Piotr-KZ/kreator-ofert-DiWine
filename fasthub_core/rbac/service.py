"""
Logika RBAC — sprawdzanie uprawnień, przypisywanie ról, seedowanie.
To jest SERCE systemu uprawnień.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional, Set, List
from uuid import UUID

from fasthub_core.rbac.models import Permission, Role, RolePermission, UserRole
from fasthub_core.rbac.defaults import CORE_PERMISSIONS, SYSTEM_ROLES


class RBACService:
    """Serwis zarządzania rolami i uprawnieniami"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # === SPRAWDZANIE UPRAWNIEŃ ===

    async def check_permission(
        self, user_id: UUID, organization_id: UUID, permission: str
    ) -> bool:
        """
        Sprawdza czy user ma dane uprawnienie w organizacji.
        Używane jako: if await rbac.check_permission(user.id, org.id, "processes.edit"):
        """
        # Owner shortcut: Właściciel always has all permissions
        owner_name = SYSTEM_ROLES["owner"]["name"]
        owner_check = await self.db.execute(
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == user_id,
                UserRole.organization_id == organization_id,
                Role.name == owner_name,
                Role.is_system == True,
            )
        )
        if owner_check.scalar_one_or_none():
            return True

        permissions = await self.get_user_permissions(user_id, organization_id)
        return permission in permissions

    async def get_user_permissions(
        self, user_id: UUID, organization_id: UUID
    ) -> Set[str]:
        """
        Zwraca ZBIÓR wszystkich uprawnień usera w organizacji.
        Agreguje permissions ze WSZYSTKICH ról usera.
        """
        query = (
            select(Permission.name)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == user_id,
                UserRole.organization_id == organization_id,
            )
        )
        result = await self.db.execute(query)
        return set(result.scalars().all())

    async def get_user_roles(
        self, user_id: UUID, organization_id: UUID
    ) -> List[dict]:
        """Zwraca listę ról usera w organizacji"""
        query = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == user_id,
                UserRole.organization_id == organization_id,
            )
        )
        result = await self.db.execute(query)
        roles = result.scalars().all()
        return [{"id": r.id, "name": r.name, "is_system": r.is_system} for r in roles]

    # === ZARZĄDZANIE ROLAMI ===

    async def assign_role(
        self,
        user_id: UUID,
        role_id: UUID,
        organization_id: UUID,
        assigned_by: Optional[UUID] = None,
    ) -> Optional[UserRole]:
        """Przypisz rolę użytkownikowi w organizacji"""
        existing = await self.db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
                UserRole.organization_id == organization_id,
            )
        )
        if existing.scalar_one_or_none():
            return None  # Już ma tę rolę

        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            organization_id=organization_id,
            assigned_by=assigned_by,
        )
        self.db.add(user_role)
        await self.db.flush()
        return user_role

    async def remove_role(
        self, user_id: UUID, role_id: UUID, organization_id: UUID
    ) -> bool:
        """Usuń rolę użytkownikowi"""
        result = await self.db.execute(
            delete(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
                UserRole.organization_id == organization_id,
            )
        )
        return result.rowcount > 0

    async def create_custom_role(
        self,
        organization_id: UUID,
        name: str,
        description: str,
        permission_names: List[str],
    ) -> Role:
        """
        Tworzy nową rolę custom w organizacji.
        Np. firma Budimex tworzy rolę "Kierownik Budowy" z uprawnieniami
        do procesów i monitoringu ale bez dostępu do billingu.
        """
        role = Role(
            organization_id=organization_id,
            name=name,
            description=description,
            is_system=False,
        )
        self.db.add(role)
        await self.db.flush()

        for perm_name in permission_names:
            perm = await self.db.execute(
                select(Permission).where(Permission.name == perm_name)
            )
            perm = perm.scalar_one_or_none()
            if perm:
                rp = RolePermission(role_id=role.id, permission_id=perm.id)
                self.db.add(rp)

        await self.db.flush()
        return role

    async def update_role(
        self, role_id: UUID, name: Optional[str] = None, description: Optional[str] = None
    ) -> Role:
        """Aktualizuj nazwę/opis roli (blokada dla Właściciela)"""
        role = await self.db.get(Role, role_id)
        if not role:
            raise ValueError("Rola nie znaleziona")
        owner_name = SYSTEM_ROLES["owner"]["name"]
        if role.is_system and role.name == owner_name:
            raise ValueError("Nie można modyfikować roli Właściciel")
        if name is not None:
            role.name = name
        if description is not None:
            role.description = description
        await self.db.flush()
        return role

    async def update_role_permissions(
        self, role_id: UUID, permission_names: List[str]
    ) -> None:
        """Nadpisz permissions roli (usuń stare, dodaj nowe). Edytowalne dla wszystkich ról oprócz Właściciela."""
        role = await self.db.get(Role, role_id)
        if not role:
            raise ValueError("Rola nie znaleziona")
        owner_name = SYSTEM_ROLES["owner"]["name"]
        if role.is_system and role.name == owner_name:
            raise ValueError("Nie można modyfikować uprawnień roli Właściciel")

        # Usuń stare
        await self.db.execute(
            delete(RolePermission).where(RolePermission.role_id == role_id)
        )

        # Dodaj nowe
        for perm_name in permission_names:
            perm = await self.db.execute(
                select(Permission).where(Permission.name == perm_name)
            )
            perm = perm.scalar_one_or_none()
            if perm:
                rp = RolePermission(role_id=role_id, permission_id=perm.id)
                self.db.add(rp)

        await self.db.flush()

    async def delete_role(self, role_id: UUID) -> bool:
        """Usuń rolę custom (systemowych nie można usunąć)"""
        role = await self.db.get(Role, role_id)
        if not role:
            return False
        if role.is_system:
            raise ValueError("Nie można usunąć roli systemowej")

        await self.db.delete(role)
        await self.db.flush()
        return True

    async def list_organization_roles(self, organization_id: UUID) -> List[Role]:
        """Lista ról dostępnych w organizacji (systemowe + custom)"""
        query = select(Role).where(
            (Role.organization_id == organization_id) | (Role.organization_id.is_(None))
        ).order_by(Role.is_system.desc(), Role.name)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def list_permissions(self, category: Optional[str] = None) -> List[Permission]:
        """Lista wszystkich uprawnień (opcjonalnie filtr po kategorii)"""
        query = select(Permission)
        if category:
            query = query.where(Permission.category == category)
        query = query.order_by(Permission.category, Permission.name)
        result = await self.db.execute(query)
        return result.scalars().all()

    # === SEEDOWANIE ===

    async def seed_permissions(self, extra_permissions: dict = None) -> None:
        """
        Tworzy bazowe uprawnienia w bazie danych.
        Wywoływane przy starcie aplikacji.

        extra_permissions: dodatkowe uprawnienia z aplikacji
        Np. AutoFlow dodaje:
        {
            "processes": [
                ("processes.view", "Podgląd procesów"),
                ("processes.create", "Tworzenie procesów"),
            ],
        }
        """
        all_permissions = dict(CORE_PERMISSIONS)
        if extra_permissions:
            all_permissions.update(extra_permissions)

        for category, perms in all_permissions.items():
            for name, description in perms:
                existing = await self.db.execute(
                    select(Permission).where(Permission.name == name)
                )
                if not existing.scalar_one_or_none():
                    perm = Permission(
                        name=name,
                        category=category,
                        description=description,
                        is_system=(category in CORE_PERMISSIONS),
                    )
                    self.db.add(perm)

        await self.db.commit()

    async def seed_organization_roles(self, organization_id: UUID) -> None:
        """
        Tworzy domyślne role systemowe dla nowej organizacji.
        Wywoływane przy tworzeniu organizacji.
        """
        all_perm_names = []
        for category, perms in CORE_PERMISSIONS.items():
            for name, desc in perms:
                all_perm_names.append(name)

        for role_key, role_def in SYSTEM_ROLES.items():
            existing = await self.db.execute(
                select(Role).where(
                    Role.organization_id == organization_id,
                    Role.name == role_def["name"],
                    Role.is_system == True,
                )
            )
            if existing.scalar_one_or_none():
                continue

            role = Role(
                organization_id=organization_id,
                name=role_def["name"],
                description=role_def["description"],
                is_system=role_def["is_system"],
                is_default=role_def["is_default"],
            )
            self.db.add(role)
            await self.db.flush()

            if role_def["permissions"] == "*":
                perm_names = all_perm_names
            else:
                perm_names = role_def["permissions"]

            for perm_name in perm_names:
                perm = await self.db.execute(
                    select(Permission).where(Permission.name == perm_name)
                )
                perm = perm.scalar_one_or_none()
                if perm:
                    rp = RolePermission(role_id=role.id, permission_id=perm.id)
                    self.db.add(rp)

        await self.db.commit()

    async def register_app_permissions(self, app_permissions: dict) -> None:
        """
        Rejestruje uprawnienia specyficzne dla aplikacji.
        Wywoływane przy starcie aplikacji (np. AutoFlow).
        """
        await self.seed_permissions(extra_permissions=app_permissions)
