"""
Wbudowane komendy CLI.
"""

import asyncio
import sys
import typer
from typing import Optional

from fasthub_core.cli.app import app


def _run_async(coro):
    """Helper — uruchom async funkcję w sync CLI."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# =========================================================================
# SEED
# =========================================================================

@app.command()
def seed(
    plans: bool = typer.Option(True, help="Załaduj plany billing"),
    permissions: bool = typer.Option(True, help="Załaduj uprawnienia RBAC"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Szczegółowy output"),
):
    """
    Załaduj dane początkowe (plany, role, uprawnienia).

    Przykład:
        fasthub seed                  — wszystko
        fasthub seed --no-plans       — tylko uprawnienia
        fasthub seed --no-permissions — tylko plany
    """
    async def _seed():
        from fasthub_core.db.session import get_async_session_local, init_db
        await init_db()

        session_factory = get_async_session_local()
        async with session_factory() as db:
            total = 0

            if plans:
                from fasthub_core.billing.service import BillingService
                service = BillingService(db)
                count = await service.seed_billing_plans()
                await db.commit()
                typer.echo(f"  Plany billing: {count} zaladowanych")
                total += count

            if permissions:
                from fasthub_core.rbac.service import RBACService
                service = RBACService(db)
                await service.seed_permissions()
                await db.commit()
                typer.echo(f"  Uprawnienia RBAC: zaladowane")
                total += 1

            typer.echo(f"\nSeed zakonczony ({total} operacji)")

    typer.echo("Seedowanie danych...\n")
    _run_async(_seed())


# =========================================================================
# CREATE-ADMIN
# =========================================================================

@app.command()
def create_admin(
    email: str = typer.Option(..., prompt=True, help="Email administratora"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Haslo"),
    full_name: str = typer.Option("Admin", prompt=True, help="Imie i nazwisko"),
    org_name: str = typer.Option("Default Organization", prompt=True, help="Nazwa organizacji"),
):
    """
    Stwórz pierwszego administratora + organizację.

    Przykład:
        fasthub create-admin --email admin@firma.pl --full-name "Jan Kowalski" --org-name "Firma Sp. z o.o."
    """
    async def _create():
        from fasthub_core.db.session import get_async_session_local, init_db
        from fasthub_core.users.models import User, Organization
        from fasthub_core.auth.service import get_password_hash
        from sqlalchemy import select

        await init_db()

        session_factory = get_async_session_local()
        async with session_factory() as db:
            # Sprawdź czy email zajęty
            existing = await db.execute(select(User).where(User.email == email))
            if existing.scalar_one_or_none():
                typer.echo(f"Uzytkownik {email} juz istnieje")
                raise typer.Exit(code=1)

            # Stwórz użytkownika
            user = User(
                email=email,
                hashed_password=get_password_hash(password),
                full_name=full_name,
                is_active=True,
                is_verified=True,
                is_email_verified=True,
                is_superuser=True,
                is_superadmin=True,
            )
            db.add(user)
            await db.flush()

            # Stwórz organizację
            slug = org_name.lower().replace(" ", "-").replace(".", "")[:50]
            org = Organization(
                name=org_name,
                slug=slug,
                owner_id=user.id,
                is_complete=True,
            )
            db.add(org)
            await db.commit()

            typer.echo(f"\nAdministrator stworzony:")
            typer.echo(f"   Email: {email}")
            typer.echo(f"   Organizacja: {org_name} (slug: {slug})")
            typer.echo(f"   User ID: {user.id}")
            typer.echo(f"   Org ID: {org.id}")

    typer.echo("Tworzenie administratora...\n")
    _run_async(_create())


# =========================================================================
# CHECK
# =========================================================================

@app.command()
def check():
    """
    Sprawdź połączenia i konfigurację.

    Weryfikuje: Database, Redis, Stripe, Email, Storage.
    """
    from fasthub_core.config import get_settings
    settings = get_settings()

    typer.echo("Sprawdzanie polaczen...\n")
    all_ok = True

    # Database
    try:
        async def _check_db():
            from fasthub_core.db.session import get_engine
            from sqlalchemy import text
            engine = get_engine()
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True

        _run_async(_check_db())
        typer.echo(f"  [OK] Database: ({settings.DATABASE_URL[:30]}...)")
    except Exception as e:
        typer.echo(f"  [FAIL] Database: {e}")
        all_ok = False

    # Redis
    try:
        async def _check_redis():
            from fasthub_core.infrastructure.redis import get_redis
            redis = await get_redis()
            await redis.ping()
            return True

        if settings.REDIS_URL:
            _run_async(_check_redis())
            typer.echo(f"  [OK] Redis: ({settings.REDIS_URL})")
        else:
            typer.echo(f"  [WARN] Redis: nie skonfigurowany (REDIS_URL)")
    except Exception as e:
        typer.echo(f"  [FAIL] Redis: {e}")
        all_ok = False

    # Stripe
    if settings.STRIPE_SECRET_KEY:
        typer.echo(f"  [OK] Stripe: klucz skonfigurowany (sk_...{settings.STRIPE_SECRET_KEY[-4:]})")
    else:
        typer.echo(f"  [WARN] Stripe: brak STRIPE_SECRET_KEY")

    # Email
    if getattr(settings, "SMTP_HOST", None):
        typer.echo(f"  [OK] Email: SMTP ({settings.SMTP_HOST})")
    else:
        typer.echo(f"  [WARN] Email: Console (brak SMTP_HOST)")

    # Storage
    if getattr(settings, "AWS_S3_BUCKET", None):
        typer.echo(f"  [OK] Storage: S3 ({settings.AWS_S3_BUCKET})")
    else:
        typer.echo(f"  [WARN] Storage: Local (brak AWS_S3_BUCKET)")

    # Task queue
    task_backend = getattr(settings, "TASK_BACKEND", "sync")
    typer.echo(f"  [{'OK' if task_backend != 'sync' else 'WARN'}] Task Queue: {task_backend}")

    # Summary
    typer.echo("")
    if all_ok:
        typer.echo("Wszystko OK!")
    else:
        typer.echo("Niektore polaczenia maja problemy")
        raise typer.Exit(code=1)


# =========================================================================
# SHOW-CONFIG
# =========================================================================

@app.command()
def show_config(
    secrets: bool = typer.Option(False, "--secrets", help="Pokaz sekrety (uwaga!)"),
):
    """
    Pokaż aktualną konfigurację FastHub.
    """
    from fasthub_core.config import get_settings
    settings = get_settings()

    typer.echo("Konfiguracja FastHub:\n")

    def _mask(value):
        if not value or secrets:
            return value
        s = str(value)
        if len(s) > 8:
            return s[:4] + "***" + s[-4:]
        return "***"

    config_items = [
        ("Environment", getattr(settings, "ENVIRONMENT", "development")),
        ("Database", settings.DATABASE_URL),
        ("Redis", getattr(settings, "REDIS_URL", "not set")),
        ("Secret Key", _mask(settings.SECRET_KEY)),
        ("Stripe Key", _mask(getattr(settings, "STRIPE_SECRET_KEY", "not set"))),
        ("SMTP Host", getattr(settings, "SMTP_HOST", "not set")),
        ("Storage", getattr(settings, "STORAGE_BACKEND", "local")),
        ("Task Backend", getattr(settings, "TASK_BACKEND", "arq")),
        ("S3 Bucket", getattr(settings, "AWS_S3_BUCKET", "not set")),
        ("Fakturownia", getattr(settings, "FAKTUROWNIA_ACCOUNT", "not set")),
    ]

    for name, value in config_items:
        typer.echo(f"  {name:20s} {value}")


# =========================================================================
# SHELL
# =========================================================================

@app.command()
def shell():
    """
    Interaktywna konsola z załadowanymi modelami FastHub.

    Dostępne obiekty:
        User, Organization, Member — modele
        BillingPlan, Subscription — modele billing
        select — SQLAlchemy select
    """
    typer.echo("FastHub Shell\n")
    typer.echo("   Dostepne: User, Organization, Member, BillingPlan, Subscription")
    typer.echo("   Tip: uzyj 'await db.execute(select(User).limit(5))'\n")

    try:
        import IPython
        # Przygotuj namespace
        from fasthub_core.users.models import User, Organization, Member
        from fasthub_core.billing.models import BillingPlan, Subscription
        from sqlalchemy import select

        namespace = {
            "User": User,
            "Organization": Organization,
            "Member": Member,
            "BillingPlan": BillingPlan,
            "Subscription": Subscription,
            "select": select,
        }

        IPython.start_ipython(argv=[], user_ns=namespace)
    except ImportError:
        typer.echo("Zainstaluj IPython dla lepszego shell: pip install ipython")
        import code
        code.interact(local=locals())
