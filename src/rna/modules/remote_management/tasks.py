import subprocess

from rna.extensions import celery, db
from rna.modules.remote_management.models import HostCommandEvent


@celery.task(bind=True, queue='execute_host_command')
def execute_host_command(self, hostname, command, host_command_id):
    result = subprocess.Popen("ssh {host} {cmd}".format(host=hostname, cmd=command), shell=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(timeout=30)
    stdout, stderr = result
    if host_command_id:
        event = HostCommandEvent(result=stdout.decode() + '\n' + stderr.decode(), host_command_id=host_command_id)
        db.session.add(event)
        db.session.commit()
    return stdout.decode() + '\n' + stderr.decode()
