import atexit
import os
import sys

from django.contrib.staticfiles.management.commands.runserver import (
    Command as StaticFilesRunserverCommand,
)

from django_wind.cli import ensure_cli, run_watch
from django_wind.conf import get_config
from django_wind.discovery import generate_input_css

_tailwind_proc = None


def _start_tailwind():
    global _tailwind_proc
    config = get_config()

    try:
        cli = ensure_cli(config)
    except Exception as e:
        print(f"[django-wind] Could not start Tailwind: {e}", file=sys.stderr)
        return

    input_css = generate_input_css(config)
    output_css = config.output_css_path
    _tailwind_proc = run_watch(cli, input_css, output_css)
    print(f"[django-wind] Tailwind watching -> {output_css}")

    def _cleanup():
        if _tailwind_proc and _tailwind_proc.poll() is None:
            _tailwind_proc.terminate()
            _tailwind_proc.wait()

    atexit.register(_cleanup)


class Command(StaticFilesRunserverCommand):

    def inner_run(self, *args, **options):
        # inner_run is called in the child process (with reloader)
        # or directly (with --noreload). Either way, start Tailwind here.
        if _tailwind_proc is None:
            _start_tailwind()
        super().inner_run(*args, **options)
