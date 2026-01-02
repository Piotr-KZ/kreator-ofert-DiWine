"""
Create demo data for AutoFlow SaaS application
Generates realistic users, organizations, memberships, and subscriptions
"""

import asyncio
import sys
from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add app to path
sys.path.insert(0, "/home/ubuntu/fasthub-repo/fasthub-backend")

from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.member import Member, MemberRole
from app.models.organization import Organization
from app.models.subscription import Subscription
from app.models.user import User


# Demo data
DEMO_ORGANIZATIONS = [
    {"name": "TechCorp Solutions", "slug": "techcorp-solutions"},
    {"name": "Digital Innovations Ltd", "slug": "digital-innovations"},
    {"name": "CloudStart Inc", "slug": "cloudstart"},
    {"name": "DataFlow Systems", "slug": "dataflow-systems"},
]

DEMO_USERS = [
    {
        "full_name": "Alice Johnson",
        "email": "alice.johnson@techcorp.com",
        "org_index": 0,
        "role": MemberRole.ADMIN,
    },
    {
        "full_name": "Bob Smith",
        "email": "bob.smith@techcorp.com",
        "org_index": 0,
        "role": MemberRole.VIEWER,
    },
    {
        "full_name": "Carol Williams",
        "email": "carol.williams@digitalinnovations.com",
        "org_index": 1,
        "role": MemberRole.ADMIN,
    },
    {
        "full_name": "David Brown",
        "email": "david.brown@digitalinnovations.com",
        "org_index": 1,
        "role": MemberRole.VIEWER,
    },
    {
        "full_name": "Emma Davis",
        "email": "emma.davis@digitalinnovations.com",
        "org_index": 1,
        "role": MemberRole.VIEWER,
    },
    {
        "full_name": "Frank Miller",
        "email": "frank.miller@cloudstart.io",
        "org_index": 2,
        "role": MemberRole.ADMIN,
    },
    {
        "full_name": "Grace Wilson",
        "email": "grace.wilson@cloudstart.io",
        "org_index": 2,
        "role": MemberRole.VIEWER,
    },
    {
        "full_name": "Henry Moore",
        "email": "henry.moore@dataflow.systems",
        "org_index": 3,
        "role": MemberRole.ADMIN,
    },
    {
        "full_name": "Iris Taylor",
        "email": "iris.taylor@dataflow.systems",
        "org_index": 3,
        "role": MemberRole.VIEWER,
    },
    {
        "full_name": "Jack Anderson",
        "email": "jack.anderson@dataflow.systems",
        "org_index": 3,
        "role": MemberRole.VIEWER,
    },
]

DEMO_SUBSCRIPTIONS = [
    {"org_index": 0, "plan": "pro", "status": "active"},  # TechCorp - Pro
    {"org_index": 1, "plan": "enterprise", "status": "active"},  # Digital Innovations - Enterprise
    {"org_index": 2, "plan": "free", "status": "active"},  # CloudStart - Free
    {"org_index": 3, "plan": "pro", "status": "active"},  # DataFlow - Pro
]

# Default password for all demo users
DEMO_PASSWORD = "DemoPass123"


async def create_demo_data():
    """Create all demo data"""
    # Create async session
    from app.db.session import get_async_session_local
    session_local = get_async_session_local()
    async with session_local() as db:
        try:
            print("🚀 Starting demo data creation...\n")

            # Step 1: Create organizations
            print("📦 Creating organizations...")
            organizations = []
            for org_data in DEMO_ORGANIZATIONS:
                org = Organization(
                    id=uuid4(),
                    name=org_data["name"],
                    slug=org_data["slug"],
                    is_complete=True,
                    created_at=datetime.utcnow() - timedelta(days=30),  # Created 30 days ago
                )
                db.add(org)
                organizations.append(org)
                print(f"  ✅ {org.name}")

            await db.flush()  # Get IDs

            # Step 2: Create users and memberships
            print("\n👥 Creating users and memberships...")
            users = []
            hashed_password = get_password_hash(DEMO_PASSWORD)

            for user_data in DEMO_USERS:
                # Create user
                user = User(
                    id=uuid4(),
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    hashed_password=hashed_password,
                    is_active=True,
                    is_verified=True,
                    is_superuser=False,
                    created_at=datetime.utcnow() - timedelta(days=25),  # Created 25 days ago
                )
                db.add(user)
                users.append(user)

                # Create membership
                org = organizations[user_data["org_index"]]
                member = Member(
                    id=uuid4(),
                    user_id=user.id,
                    organization_id=org.id,
                    role=user_data["role"],
                    joined_at=datetime.utcnow() - timedelta(days=20),  # Joined 20 days ago
                )
                db.add(member)

                print(f"  ✅ {user.full_name} ({user.email}) - {org.name} [{user_data['role'].value}]")

            await db.flush()

            # Step 3: Subscriptions skipped (mock endpoint already works)
            print("\n💳 Subscriptions: Using mock endpoint (no Stripe data needed)")

            # Commit all changes
            await db.commit()

            print("\n✅ Demo data created successfully!")
            print(f"\n📊 Summary:")
            print(f"  - Organizations: {len(organizations)}")
            print(f"  - Users: {len(users)}")
            print(f"  - Memberships: {len(DEMO_USERS)}")
            print(f"  - Subscriptions: Mock (no real data needed)")
            print(f"\n🔑 Demo credentials:")
            print(f"  - Email: Any email from the list above")
            print(f"  - Password: {DEMO_PASSWORD}")
            print(f"\n📝 Example logins:")
            for user_data in DEMO_USERS[:3]:
                print(f"  - {user_data['email']} / {DEMO_PASSWORD}")

        except Exception as e:
            print(f"\n❌ Error creating demo data: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(create_demo_data())
