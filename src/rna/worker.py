import rna.modules.remote_management.tasks  # noqa
from rna.app import create_app
from rna.extensions import celery

app = create_app(None)
app.app_context().push()


@celery.task()
def phony():
    pass
