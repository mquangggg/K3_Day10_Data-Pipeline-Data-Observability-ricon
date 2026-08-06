from __future__ import annotations

import sys
from pathlib import Path

# Add src/ to python path
src_dir = Path(__file__).resolve().parent.parent / "src"
sys.path.append(str(src_dir))

from pipelines.corruption_flow import main


if __name__ == "__main__":
    main()
