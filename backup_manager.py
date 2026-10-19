import os
import shutil
import time
from typing import Optional

def create_timestamped_backup(filepath: str, timestamp_str: Optional[str] = None) -> Optional[str]:
    """Cria uma cópia de segurança no padrão <filepath>.bak_YYYYMMDD_HHMMSS."""
    if not os.path.exists(filepath):
        return None

    if timestamp_str is None:
        timestamp_str = time.strftime("%Y%m%d_%H%M%S")

    backup_path = f"{filepath}.bak_{timestamp_str}"
    shutil.copy2(filepath, backup_path)
    return backup_path