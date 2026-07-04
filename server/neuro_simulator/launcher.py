"""Convenient launcher for the bundled Neuro Simulator web UI."""

from __future__ import annotations

import argparse
import os
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Optional



def _open_browser_later(url: str, delay: float) -> None:
    """Open the browser after uvicorn has had a moment to bind the socket."""
    time.sleep(delay)
    webbrowser.open(url)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch Neuro Simulator with the bundled web UI")
    parser.add_argument(
        "--dir",
        "-D",
        default="~/.config/neuro-simulator",
        help="Working directory (default: ~/.config/neuro-simulator)",
    )
    parser.add_argument("--host", help="Override host from config.json")
    parser.add_argument("--port", type=int, help="Override port from config.json")
    parser.add_argument("--reload", action="store_true", help="Enable uvicorn reload mode for development")
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open the dashboard in the default browser after startup",
    )
    parser.add_argument(
        "--browser-delay",
        type=float,
        default=1.0,
        help="Seconds to wait before opening the browser (default: 1.0)",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> None:
    args = build_parser().parse_args(argv)

    import uvicorn

    from neuro_simulator.vedal_studio.api import app_state
    from neuro_simulator.vedal_studio.config import ConfigManager, WorkingDirManager
    from neuro_simulator.vedal_studio.main import create_app

    working_dir = os.path.expanduser(args.dir)
    WorkingDirManager(working_dir).setup_working_dir()

    config_manager = ConfigManager(working_dir)
    server_settings = config_manager.config.get("general", {}).get("server_settings", {})
    host = args.host or server_settings.get("host", "127.0.0.1")
    port = args.port if args.port is not None else server_settings.get("port", 8000)

    app_state["config_manager"] = config_manager
    app = create_app(working_dir)

    url = f"http://{host}:{port}/"
    print(f"Neuro Simulator launcher starting at {url}")
    print(f"Working directory: {Path(working_dir)}")
    print("Press Ctrl+C to stop.")

    if not args.no_browser:
        threading.Thread(target=_open_browser_later, args=(url, args.browser_delay), daemon=True).start()

    if args.reload:
        # Uvicorn reload needs an import string instead of an app instance.
        sys.argv = [sys.argv[0], "--dir", working_dir]
        uvicorn.run(
            "neuro_simulator.vedal_studio.main:get_app",
            host=host,
            port=port,
            reload=True,
        )
    else:
        uvicorn.run(app, host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
