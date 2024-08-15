from pathlib import Path
import sys

mock_path = Path(__file__).parents[3] / "tests/mocks"

sys.path.insert(1, str(mock_path))
import scripting_toolkit  # noqa: F401
