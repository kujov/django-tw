from pathlib import Path

from django.apps import apps
from django.conf import settings

from .conf import WindConfig


def discover_template_dirs() -> list[Path]:
    dirs: set[Path] = set()

    for tpl_config in settings.TEMPLATES:
        # Explicit DIRS
        for d in tpl_config.get("DIRS", []):
            p = Path(d)
            if p.is_dir():
                dirs.add(p.resolve())

        # APP_DIRS: scan each installed app for a templates/ folder
        if tpl_config.get("APP_DIRS", False):
            for app_config in apps.get_app_configs():
                tpl_dir = Path(app_config.path) / "templates"
                if tpl_dir.is_dir():
                    dirs.add(tpl_dir.resolve())

    return sorted(dirs)


def generate_input_css(config: WindConfig) -> Path:
    template_dirs = discover_template_dirs()

    lines = ['@import "tailwindcss";', ""]
    for d in template_dirs:
        lines.append(f'@source "{d}/**/*.html";')

    for pattern in config.extra_sources:
        lines.append(f'@source "{pattern}";')

    css_path = config.input_css_path
    css_path.parent.mkdir(parents=True, exist_ok=True)
    css_path.write_text("\n".join(lines) + "\n")
    return css_path
