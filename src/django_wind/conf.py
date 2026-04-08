from dataclasses import dataclass, field
from pathlib import Path

from django.conf import settings


@dataclass
class WindConfig:
    output_css: str = "css/wind.css"
    cli_version: str = "latest"
    cli_path: str | None = None
    extra_sources: list[str] = field(default_factory=list)
    extra_css: list[str] = field(default_factory=list)
    input_css: str | None = None

    @property
    def base_dir(self) -> Path:
        return Path(settings.BASE_DIR)

    @property
    def dot_wind_dir(self) -> Path:
        d = self.base_dir / ".wind"
        d.mkdir(exist_ok=True)
        return d

    @property
    def input_css_path(self) -> Path:
        if self.input_css:
            return Path(self.input_css)
        return self.dot_wind_dir / "input.css"

    @property
    def output_css_path(self) -> Path:
        static_dirs = getattr(settings, "STATICFILES_DIRS", [])
        if static_dirs:
            return Path(static_dirs[0]) / self.output_css
        return self.base_dir / "static" / self.output_css

    @property
    def bin_dir(self) -> Path:
        d = self.dot_wind_dir / "bin"
        d.mkdir(parents=True, exist_ok=True)
        return d


def get_config() -> WindConfig:
    overrides = getattr(settings, "WIND", {})
    return WindConfig(
        output_css=overrides.get("OUTPUT_CSS", "css/wind.css"),
        cli_version=overrides.get("CLI_VERSION", "latest"),
        cli_path=overrides.get("CLI_PATH"),
        extra_sources=overrides.get("EXTRA_SOURCES", []),
        extra_css=overrides.get("EXTRA_CSS", []),
        input_css=overrides.get("INPUT_CSS"),
    )
