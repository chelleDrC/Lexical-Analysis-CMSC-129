"""Entry point for the PE03 predictive parser (Member 4).

Run with:  python main.py
"""

from controller import Controller
from view import View


def main() -> None:
    view = View()
    Controller(view)
    view.run()


if __name__ == "__main__":
    main()
