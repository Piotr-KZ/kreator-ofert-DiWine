"""
User flow integration tests — register, login, project CRUD, password change,
token refresh, organization isolation.
"""

import pytest
from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.member import Member
from app.models.project import Project


# ─── helpers ───

async def register_user(client, email: str, password: str, full_name: str, org_name: str):
    """Register a new user and return the response JSON."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": full_name,
            "organization_name": org_name,
        },
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.text
    return resp.json()


async def login_user(client, email: str, password: str):
    """Login and return the response JSON (tokens)."""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.text
    return resp.json()


async def auth_headers_from(client, db: AsyncSession, email: str, password: str) -> dict:
    """Login and build auth headers with X-Organization-Id."""
    tokens = await login_user(client, email, password)
    # Fetch org_id from Member table
    from app.models.user import User
    user_row = (await db.execute(select(User).where(User.email == email))).scalar_one()
    member_row = (await db.execute(
        select(Member).where(Member.user_id == user_row.id)
    )).scalar_one()
    return {
        "Authorization": f"Bearer {tokens['access_token']}",
        "X-Organization-Id": str(member_row.organization_id),
    }


# ============================================================================
# 1. Basic user → project flow
# ============================================================================

class TestBasicUserProjectFlow:
    """Register → login → GET /me → create project → list → get."""

    @pytest.mark.asyncio
    async def test_full_flow(self, async_client, db_session):
        ac = async_client
        db = db_session

        # ── register ──
        reg = await register_user(ac, "flow@example.com", "FlowPass123", "Flow User", "Flow Org")
        assert "access_token" in reg
        assert "refresh_token" in reg
        assert reg["token_type"] == "bearer"

        # ── login ──
        tokens = await login_user(ac, "flow@example.com", "FlowPass123")
        assert "access_token" in tokens

        # ── resolve org_id from DB ──
        headers = await auth_headers_from(ac, db, "flow@example.com", "FlowPass123")

        # ── GET /me ──
        me = await ac.get("/api/v1/auth/me", headers=headers)
        assert me.status_code == 200
        assert me.json()["email"] == "flow@example.com"
        assert me.json()["full_name"] == "Flow User"

        # ── create project ──
        create_resp = await ac.post(
            "/api/v1/creator/projects",
            headers=headers,
            json={"name": "My Website", "site_type": "firmowa"},
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        project = create_resp.json()
        project_id = project["id"]
        assert project["name"] == "My Website"
        assert project["status"] == "draft"

        # ── list projects ──
        list_resp = await ac.get("/api/v1/creator/projects", headers=headers)
        assert list_resp.status_code == 200
        projects = list_resp.json()
        assert any(p["id"] == project_id for p in projects)

        # ── get single project ──
        get_resp = await ac.get(f"/api/v1/creator/projects/{project_id}", headers=headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == project_id


# ============================================================================
# 2. Company registration with NIP / REGON
# ============================================================================

class TestCompanyRegistration:
    """Register with business fields and verify organization in DB."""

    @pytest.mark.asyncio
    async def test_business_registration(self, async_client, db_session):
        ac = async_client
        db = db_session

        resp = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": "firma@example.com",
                "password": "FirmaPass123",
                "full_name": "Jan Kowalski",
                "organization_name": "Firma Sp. z o.o.",
                "account_type": "business",
                "nip": "1234567890",
                "regon": "123456789",
            },
        )
        assert resp.status_code == status.HTTP_201_CREATED

        # Verify organization fields in DB
        from app.models.organization import Organization
        from app.models.user import User

        user = (await db.execute(select(User).where(User.email == "firma@example.com"))).scalar_one()
        member = (await db.execute(select(Member).where(Member.user_id == user.id))).scalar_one()
        org = (await db.execute(
            select(Organization).where(Organization.id == member.organization_id)
        )).scalar_one()

        assert org.name == "Firma Sp. z o.o."
        assert org.nip == "1234567890"
        assert org.regon == "123456789"
        assert member.role == "owner"


# ============================================================================
# 3. Password change
# ============================================================================

class TestPasswordChange:
    """Change password → old fails → new works."""

    @pytest.mark.asyncio
    async def test_change_password_flow(self, async_client, db_session):
        ac = async_client

        # Register
        await register_user(ac, "pwd@example.com", "OldPass123", "Pwd User", "Pwd Org")
        headers = await auth_headers_from(ac, db_session, "pwd@example.com", "OldPass123")

        # Change password
        resp = await ac.post(
            "/api/v1/auth/change-password",
            headers=headers,
            json={"current_password": "OldPass123", "new_password": "NewPass456"},
        )
        assert resp.status_code == 200

        # Old password should fail
        old_login = await ac.post(
            "/api/v1/auth/login",
            json={"email": "pwd@example.com", "password": "OldPass123"},
        )
        assert old_login.status_code == status.HTTP_401_UNAUTHORIZED

        # New password should work
        new_login = await ac.post(
            "/api/v1/auth/login",
            json={"email": "pwd@example.com", "password": "NewPass456"},
        )
        assert new_login.status_code == 200
        assert "access_token" in new_login.json()


# ============================================================================
# 4. Token refresh
# ============================================================================

class TestTokenRefresh:
    """Login → refresh → use new token → GET /me."""

    @pytest.mark.asyncio
    async def test_token_refresh_flow(self, async_client, db_session):
        ac = async_client

        await register_user(ac, "refresh@example.com", "RefreshPass123", "Refresh User", "Refresh Org")
        tokens = await login_user(ac, "refresh@example.com", "RefreshPass123")

        # Refresh token
        refresh_resp = await ac.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert refresh_resp.status_code == 200
        new_tokens = refresh_resp.json()
        assert "access_token" in new_tokens
        assert new_tokens["token_type"] == "bearer"

        # Use new access token to call /me
        # Resolve org_id
        from app.models.user import User
        user = (await db_session.execute(
            select(User).where(User.email == "refresh@example.com")
        )).scalar_one()
        member = (await db_session.execute(
            select(Member).where(Member.user_id == user.id)
        )).scalar_one()

        new_headers = {
            "Authorization": f"Bearer {new_tokens['access_token']}",
            "X-Organization-Id": str(member.organization_id),
        }
        me = await ac.get("/api/v1/auth/me", headers=new_headers)
        assert me.status_code == 200
        assert me.json()["email"] == "refresh@example.com"


# ============================================================================
# 5. Organization isolation
# ============================================================================

class TestOrganizationIsolation:
    """User A and B in different orgs — A's project invisible to B."""

    @pytest.mark.asyncio
    async def test_org_isolation(self, async_client, db_session):
        ac = async_client
        db = db_session

        # Register two users in separate orgs
        await register_user(ac, "alice@example.com", "AlicePass123", "Alice", "Org Alpha")
        await register_user(ac, "bob@example.com", "BobPass123", "Bob", "Org Beta")

        headers_a = await auth_headers_from(ac, db, "alice@example.com", "AlicePass123")
        headers_b = await auth_headers_from(ac, db, "bob@example.com", "BobPass123")

        # Alice creates a project
        create_resp = await ac.post(
            "/api/v1/creator/projects",
            headers=headers_a,
            json={"name": "Alice Secret Site", "site_type": "firmowa"},
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        project_id = create_resp.json()["id"]

        # Bob lists projects — should be empty
        bob_list = await ac.get("/api/v1/creator/projects", headers=headers_b)
        assert bob_list.status_code == 200
        bob_projects = bob_list.json()
        assert not any(p["id"] == project_id for p in bob_projects)

        # Bob tries direct access — should get 404
        bob_direct = await ac.get(f"/api/v1/creator/projects/{project_id}", headers=headers_b)
        assert bob_direct.status_code == status.HTTP_404_NOT_FOUND
