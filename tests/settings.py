import os

os.environ["DATABASE_URL"] = "sqlite://:memory:"
os.environ["DJANGO_SECRET_KEY"] = "test-secret"
os.environ["Q_CLUSTER"] = '{"sync": true, "timeout": 3600,  "retry": 3700}'
from iscc_service_generator.settings import *
