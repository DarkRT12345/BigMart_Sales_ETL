from pathlib import Path
import os
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
SQL_DIR = BASE_DIR / "sql"
ENV_PATH = BASE_DIR / ".env"

# Load environment variables from project root .env (if present).
load_dotenv(dotenv_path=ENV_PATH)

TRAIN_PATH = BASE_DIR / "data" / "raw" / "bigmart" / "train" / "bigmart_train.csv"
TEST_PATH = BASE_DIR / "data" / "raw" / "bigmart" / "test" / "bigmart_test.csv"


def get_pg_config() -> dict:
    host = os.getenv("PGHOST") or os.getenv("POSTGRES_HOST") or "localhost"
    port = os.getenv("PGPORT") or os.getenv("POSTGRES_PORT") or "5432"
    dbname = os.getenv("PGDATABASE") or os.getenv("POSTGRES_DB") or "bigmart_dw"
    user = os.getenv("PGUSER") or os.getenv("POSTGRES_USER") or "postgres"
    password = os.getenv("PGPASSWORD") or os.getenv("POSTGRES_PASSWORD") or "postgres"

    return {
        "host": host.strip(),
        "port": int(str(port).strip()),
        "dbname": dbname.strip(),
        "user": user.strip(),
        "password": str(password).strip(),
    }


def get_pg_admin_candidates(pg_config: dict) -> list[str]:
    """
    Candidate databases to connect for CREATE DATABASE operations.
    Supports:
    - PGADMIN_DB (single database name)
    - PGADMIN_DATABASES (comma-separated list)
    """
    raw = os.getenv("PGADMIN_DATABASES") or os.getenv("PGADMIN_DB") or ""
    candidates = [x.strip() for x in raw.split(",") if x.strip()]

    # Common defaults, appended after explicit config.
    candidates.extend(
        [
            pg_config["user"],  # common default DB name in managed environments
            "postgres",
            "template1",
        ]
    )

    # De-duplicate while preserving order and skipping target DB.
    unique: list[str] = []
    target_db = pg_config["dbname"]
    for name in candidates:
        if name != target_db and name not in unique:
            unique.append(name)
    return unique


def is_pg_auto_create_enabled() -> bool:
    raw = (os.getenv("PGAUTO_CREATE_DB") or "true").strip().lower()
    return raw in {"1", "true", "yes", "y", "on"}
