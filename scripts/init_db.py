from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.seed import initialize_database


if __name__ == "__main__":
    initialize_database(with_demo_data=True)
    print("数据库与示例数据初始化完成。")
