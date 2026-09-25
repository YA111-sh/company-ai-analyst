from pathlib import Path

_DIR = Path(__file__).parent / "instructions"


def load_instructions(name: str) -> str:
    return (_DIR / f"{name}.md").read_text(encoding="utf-8")


if __name__ == "__main__":
    print(load_instructions("analyst"))