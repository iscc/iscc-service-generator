from pathlib import Path
from collections import OrderedDict as OrderedDictObject
from typing import Dict, List, OrderedDict
from pydantic import BaseSettings, Field
from pydantic.fields import Undefined
from .pydjantic import BaseDBConfig, to_django
from typing import Optional


CUR_DIR = Path(__file__).resolve().parent
BASE_DIR = CUR_DIR.parent.parent


class DatabaseSettings(BaseDBConfig):
    default: str = Field(
        default=str(f"sqlite:///{BASE_DIR}/.scratch/db.sqlite3"), env="DATABASE_URL"
    )

    class Config:
        env_file = ".env"


class GeneralSettings(BaseSettings):
    FIXTURE_DIRS: List[str] = [(BASE_DIR / "iscc_service_generator/fixtures").as_posix()]
    CSRF_TRUSTED_ORIGINS: List[str] = []
    X_FRAME_OPTIONS: str = "SAMEORIGIN"
    CORS_ALLOW_ALL_ORIGINS: bool = True
    SILENCED_SYSTEM_CHECKS: List[str] = ["security.W019"]
    DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"
    SECRET_KEY: str = Field(default=Undefined, env="DJANGO_SECRET_KEY")
    DEBUG: bool = Field(default=False, env="DEBUG")
    DATABASES: DatabaseSettings = DatabaseSettings()
    SENTRY_DSN: str = Field(default="", env="SENTRY_DSN")

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
        "corsheaders",
        "django_json_widget",
        "django_object_actions",
        "iscc_generator",
        "django_q",
    ]

    MIDDLEWARE: List[str] = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "corsheaders.middleware.CorsMiddleware",
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

    # Upload file pre-processing does not work with InMemoryUploadedFile!!!
    FILE_UPLOAD_HANDLERS: List[str] = [
        "iscc_generator.uploadhandler.IsccQuotaUploadHandler",
        "django.core.files.uploadhandler.TemporaryFileUploadHandler",
    ]

    DEFAULT_FILE_STORAGE: str = "django.core.files.storage.FileSystemStorage"


class I18NSettings(BaseSettings):
    # https://docs.djangoproject.com/en/3.1/topics/i18n/
    LANGUAGE_CODE: str = "en-us"
    TIME_ZONE: str = "UTC"
    USE_I18N: bool = True
    USE_TZ: bool = True
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
        "max_attempts": 1,
        "timeout": 3600,
        "retry": 3700,
        "save_limit": 0,
        "bulk": 10,
        "orm": "default",
        "sync": False,
        "label": "Background Tasks",
        "catch_up": False,
        "daemonize_workers": False,
    }


class ConstanceSettings(BaseSettings):
    # fmt: off
    CONSTANCE_BACKEND: str = "constance.backends.database.DatabaseBackend"
    CONSTANCE_CONFIG: OrderedDict = OrderedDictObject(
        [
            ("DOMAIN", ("https://example.com", "Domain where this service is hosted", "url_field")),
            ("IPFS_WRAP", (False, "Wrap file with dicectory for IPFS URIs")),
            ("NFT_EXCLUDE_FIELDS", ("", "Comma separated list of fields to exclude from results")),
            ("DOWNLOAD_TIMEOUT", (5, "Timeout in seconds for media downloads")),
            ("DOWNLOAD_VERIFY_TLS", (True, "Verify TLS for media downloads")),
            ("DOWNLOAD_SIZE_LIMIT", (100, "Maximum size for media file downloads in MB")),
            ("PROCESSING_TIMEOUT", (10, "Seconds to wait before returning an async task")),
        ]
    )
    CONSTANCE_CONFIG_FIELDSETS: OrderedDict = OrderedDictObject([
        ("General", ("DOMAIN",)),
        ("API Settings", ("IPFS_WRAP", "NFT_EXCLUDE_FIELDS",)),
        ("Asset Downloads", ("DOWNLOAD_TIMEOUT", "DOWNLOAD_VERIFY_TLS", "DOWNLOAD_SIZE_LIMIT")),
        ("Tasks Processing", ("PROCESSING_TIMEOUT",)),
    ])
    CONSTANCE_ADDITIONAL_FIELDS: Dict = {
        "url_field": ["django.forms.fields.CharField"],
    }
    # fmt: on


class IsccGeneratorSettings(BaseSettings):
    UPLOAD_SIZE_LIMIT: int = 100
    ISCC_ID_FORECAST_URL: Optional[str] = Field(None, description="API URL for ISCC-ID forecasts")


class S3Settings(BaseSettings):
    AWS_STORAGE_BUCKET_NAME: Optional[str] = None
    AWS_S3_ENDPOINT_URL: Optional[str] = None
    AWS_S3_REGION_NAME: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None


class ProjectSettings(
    GeneralSettings,
    I18NSettings,
    StaticSettings,
    MediaSettings,
    QClusterSettings,
    ConstanceSettings,
    IsccGeneratorSettings,
    S3Settings,
):
    pass

    class Config:
        env_file = ".env"


to_django(ProjectSettings())
