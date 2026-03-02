from setuptools import setup, find_packages

setup(
    name="fasthub-core",
    version="2.0.0-alpha",
    description="Universal SaaS boilerplate - auth, users, billing, middleware",
    author="Piotr",
    packages=find_packages(include=["fasthub_core", "fasthub_core.*"]),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "sqlalchemy>=2.0.25",
        "alembic>=1.13.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "bcrypt>=4.1.2",
        "pydantic>=2.5.3",
        "pydantic-settings>=2.1.0",
        "email-validator>=2.1.0",
        "httpx>=0.26.0",
        "redis>=5.0.1",
        "cryptography>=41.0.0",
        "stripe>=7.0.0",
        "python-dotenv>=1.0.0",
        "reportlab>=4.0.9",
        "asyncpg>=0.29.0",
    ],
)
