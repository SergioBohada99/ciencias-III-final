import sys
from pathlib import Path


def _ensure_project_root_on_path() -> None:
	project_root = Path(__file__).resolve().parent
	if str(project_root) not in sys.path:
		sys.path.insert(0, str(project_root))


def main() -> None:
	_ensure_project_root_on_path()
	from app.app import RetroApp

	app = RetroApp()
	app.run()


if __name__ == "__main__":
	main()


