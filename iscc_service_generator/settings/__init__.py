from pathlib import Path
from typing import Dict, List
from pydantic import BaseSettings, Field
from pydantic.fields import Undefined
from .pydjantic import BaseDBConfig, to_django


CUR_DIR = Path(__file__).resolve().parent
BASE_DIR = CUR_DIR.parent.parent


class DatabaseSettings(BaseDBConfig):
    default: str = Field(
        default=str(f"sqlite:///{BASE_DIR}/.scratch/db.sqlite3"), env="DATABASE_URL"
    )

    class Config:
        env_file = ".env"


class GeneralSettings(BaseSettings):
    FIXTURE_DIRS: List[str] = [
        (BASE_DIR / "iscc_service_generator/fixtures").as_posix()
    ]
    CSRF_TRUSTED_ORIGINS: List[str] = []
    X_FRAME_OPTIONS: str = "SAMEORIGIN"
    SILENCED_SYSTEM_CHECKS: List[str] = ["security.W019"]
    DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"
    SECRET_KEY: str = Field(default=Undefined, env="DJANGO_SECRET_KEY")
    DEBUG: bool = Field(default=False, env="DEBUG")
    DATABASES: DatabaseSettings = DatabaseSettings()

    ALLOWED_HOSTS: List[str] = ["*"]
    ROOT_URLCONF: str = "iscc_service_generator.urls"
    WSGI_APPLICATION: str = "iscc_service_generator.wsgi.application"

    INSTALLED_APPS: List[str] = [
        "constance",
        "constance.backends.database",
        "admin_interface",
        "colorfield",
        "iscc_service_generator.apps.GeneratorAdminConfig",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django_json_widget",
        "django_object_actions",
        "iscc_generator",
        "django_q",
    ]

    MIDDLEWARE: List[str] = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

    AUTH_PASSWORD_VALIDATORS: List[Dict] = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
    ]


class I18NSettings(BaseSettings):
    # https://docs.djangoproject.com/en/3.1/topics/i18n/
    LANGUAGE_CODE: str = "en-us"
    TIME_ZONE: str = "UTC"
    USE_I18N: bool = True
    USE_TZ: bool = True
    USE_L10N: bool = False
    DATETIME_FORMAT: str = "Y-m-d H:i:s"


class StaticSettings(BaseSettings):
    # https://docs.djangoproject.com/en/3.1/howto/static-files/
    STATIC_URL: str = "static/"
    STATIC_ROOT: str = (BASE_DIR / ".scratch/static").as_posix()

    TEMPLATES: List[Dict] = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]


class MediaSettings(BaseSettings):
    MEDIA_ROOT: str = (BASE_DIR / ".scratch/media").as_posix()
    MEDIA_URL: str = "media/"


class QClusterSettings(BaseSettings):
    Q_CLUSTER: Dict = {
        "name": "DjangORM",
        "workers": 4,
        "timeout": 90,
        "retry": 120,
        "queue_limit": 50,
        "bulk": 10,
        "orm": "default",
        "sync": True,
    }


class ConstanceSettings(BaseSettings):
    CONSTANCE_BACKEND: str = "constance.backends.database.DatabaseBackend"
    CONSTANCE_CONFIG: Dict = {
        "PREVIEW_IMAGE_SIZE": (
            128,
            "Size of generated preview images in number of pixels (not implemented yet)",
        ),
        "ENABLE_GRANULAR_FEATURES": (
            False,
            "Calculate granular features for media assets",
        ),
        "PROCESSING_TIMEOUT": (
            5,
            "Number of seconds to wait before returning a task instead of the actual result",
        ),
        "ENABLE_LIST_ENDPOINTS": (
            False,
            "Enables REST Api endpoints that can list objects "
            "(do not enable on public instances without authentication) (not implemented yet)",
        ),
        "RESULT_HOOK_URL": (
            "none",
            "An URL to which the background processing results should be deliverd "
            "(must be a an endpoint accepting POST requests with a json body) (not implemented yet)",
            "url_field",
        ),
        "RATE_LIMIT": (
            "16/m",
            "IP based rate limit for API calls (not implemented yet)",
            "rate_limit_field",
        ),
    }
    CONSTANCE_ADDITIONAL_FIELDS: Dict = {
        "url_field": ["django.forms.fields.CharField"],
        "rate_limit_field": [
            "django.forms.fields.ChoiceField",
            {
                "widget": "django.forms.Select",
                "choices": (
                    ("4/m", "4 requests per minute"),
                    ("8/m", "8 requests per minute"),
                    ("16/m", "16 requests per minute"),
                    ("32/m", "32 requests per minute"),
                    ("64/m", "64 requests per minute"),
                    ("128/m", "128 requests per minute"),
                    ("254/m", "254 requests per minute"),
                    ("512/m", "512 requests per minute"),
                    ("1024/m", "1024 requests per minute"),
                ),
            },
        ],
    }


class ProjectSettings(
    GeneralSettings,
    I18NSettings,
    StaticSettings,
    MediaSettings,
    QClusterSettings,
    ConstanceSettings,
):
    pass

    class Config:
        env_file = ".env"


to_django(ProjectSettings())