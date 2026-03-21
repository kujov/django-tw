import signal
import sys

from django.core.management.base import BaseCommand

from django_wind.cli import ensure_cli, run_build, run_watch
from django_wind.conf import get_config
from django_wind.discovery import discover_template_dirs, generate_input_css


class Command(BaseCommand):
    help = "Tailwind CSS v4 - zero config"

    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            choices=["start", "build", "download"],
            help="start (watch), build (production), or download (CLI only)",
        )

    def handle(self, *args, **options):
        action = options["action"]
        config = get_config()

        if action == "download":
            cli = ensure_cli(config, stdout_write=self.stdout.write)
            self.stdout.write(f"CLI ready at {cli}")
            return

        # Ensure CLI
        cli = ensure_cli(config, stdout_write=self.stdout.write)

        # Discover and generate input CSS
        template_dirs = discover_template_dirs()
        self.stdout.write(f"Found {len(template_dirs)} template directories:")
        for d in template_dirs:
            self.stdout.write(f"  {d}")

        input_css = generate_input_css(config)
        output_css = config.output_css_path
        self.stdout.write(f"\nInput:  {input_css}")
        self.stdout.write(f"Output: {output_css}\n")

        if action == "build":
            run_build(cli, input_css, output_css)
            size = output_css.stat().st_size
            self.stdout.write(self.style.SUCCESS(f"Built {output_css} ({size:,} bytes)"))

        elif action == "start":
            self.stdout.write("Watching for changes... (Ctrl+C to stop)\n")
            proc = run_watch(cli, input_css, output_css)

            def _shutdown(sig, frame):
                proc.terminate()
                proc.wait()
                sys.exit(0)

            signal.signal(signal.SIGINT, _shutdown)
            signal.signal(signal.SIGTERM, _shutdown)
            proc.wait()
