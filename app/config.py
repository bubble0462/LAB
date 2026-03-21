from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Settings:
    project_name: str
    database_url: str
    secret_key: str
    default_page_size: int


def get_settings() -> Settings:
    default_database_path = (DATA_DIR / "lab_inventory.db").as_posix()
    page_size_raw = os.getenv("PAGE_SIZE", "10").strip()

    try:
        page_size = max(int(page_size_raw), 1)
    except ValueError:
        page_size = 10

    return Settings(
        project_name="实验室器件局域网共享管理系统",
        database_url=os.getenv("DATABASE_URL", f"sqlite:///{default_database_path}"),
        secret_key=os.getenv("SECRET_KEY", "lab-inventory-change-this"),
        default_page_size=page_size,
    )


settings = get_settings()

