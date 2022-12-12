import os
import re
import requests
import tarfile

from slivka.scheduler.runners import Runner, Job
from slivka.utils import JobStatus


class JPredRunner(Runner):
    _jpred4="http://www.compbio.dundee.ac.uk/jpred4"
    _host = "http://www.compbio.dundee.ac.uk/jpred4/cgi-bin/rest"
    FAILED_ID = 'jp_fail'

    def submit(self, command):
        cmd, cwd = command
        with open(cmd[-1]) as fp:
            seq = fp.read()
        content = str.join("£€£€", [*cmd[1:-1], seq])
        response = requests.post(
            '%s/job' % self._host,
            data=content.encode(),
            headers={'Content-type': 'text/txt'}
        )
        response.raise_for_status()
        result_url = response.headers['Location']
        with open(os.path.join(cwd, 'stdout'), 'wb') as fp:
            fp.write(response.content)
        try:
            job_id = re.search(r'jp_.*$', result_url).group()
        except AttributeError:
            job_id = self.FAILED_ID
        return Job(job_id, cwd)

    @classmethod
    def check_status(cls, job) -> JobStatus:
        job_id, cwd = job
        if job_id == cls.FAILED_ID:
            return JobStatus.FAILED
        tarball = os.path.join(cwd, 'result.tar.gz')
        if os.path.exists(tarball):
            return JobStatus.COMPLETED
        response = requests.get('%s/job/id/%s' % (cls._host, job_id))
        response.raise_for_status()
        if "finished" not in response.text:
            return JobStatus.RUNNING
        archive_url = '{0}/results/{1}/{1}.tar.gz'.format(cls._jpred4, job_id)
        arch_response = requests.get(archive_url, stream=True)
        arch_response.raise_for_status()
        with open(tarball, 'wb') as fp:
            for chunk in arch_response.iter_content(chunk_size=4096):
                fp.write(chunk)
        with tarfile.open(tarball) as archive:
            try:
                safe_tar_extractall(archive, cwd)
            except Exception:
                return JobStatus.ERROR
        return JobStatus.COMPLETED


def safe_tar_extractall(tar: tarfile.TarFile, path='.'):
    abs_directory = os.path.abspath(path)
    for member in tar.getmembers():
        abs_target = os.path.abspath(os.path.join(path, member.name))
        prefix = os.path.commonprefix([abs_directory, abs_target])
        if prefix != abs_directory:
            raise Exception("Attempted path traversal in tar file")
    tar.extractall(path)
