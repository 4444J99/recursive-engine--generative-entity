"""
RE:GE Main Entrypoint.

Allows running the CLI as a python module:
python -m rege [command]
"""

from rege.cli import main

if __name__ == "__main__":
    main()
