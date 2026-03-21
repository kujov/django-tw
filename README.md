# django-wind

Zero-config Tailwind CSS v4 for Django. Auto-downloads the standalone CLI, discovers your templates, and watches for changes when you run `runserver`.

No Node.js. No config files. No build step to remember.

## Setup

```bash
pip install django-wind
```

Add it to the top of `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    "django_wind",
    # ...
]
```

Add the template tag to your base template:

```html
{% load wind %}
{% wind_css %}
```

## Usage

Start your dev server as usual:

```bash
python manage.py runserver
```

Tailwind starts automatically in watch mode. Edit your templates, the CSS rebuilds.

For production:

```bash
python manage.py tailwind build
```

## How it works

1. Downloads the Tailwind v4 standalone CLI on first run (cached at `~/.django-wind/bin/`)
2. Scans `TEMPLATES` and `INSTALLED_APPS` to find all template directories
3. Generates an input CSS file with `@source` directives pointing to your templates
4. Outputs to `static/css/wind.css`

## Settings

All optional. Add a `WIND` dict to your Django settings:

```python
WIND = {
    "OUTPUT_CSS": "css/wind.css",       # path relative to STATICFILES_DIRS[0]
    "CLI_VERSION": "v4.2.2",            # pin a version (default: "latest")
    "CLI_PATH": "/usr/local/bin/tw",    # use a pre-installed binary
    "EXTRA_SOURCES": [                  # additional source globs
        "/path/to/extra/templates/**/*.html",
    ],
}
```

## License

MIT
