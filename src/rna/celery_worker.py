from rna.app import create_app
from rna.extensions import celery  # noqa

app = create_app(None)
