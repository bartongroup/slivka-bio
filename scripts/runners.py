import os
import re
import requests
import tarfile

from slivka.scheduler import Runner
from slivka.utils import JobStatus


class JPredRunner(Runner):
    _jpred4="http://www.compbio.dundee.ac.uk/jpred4"
    _host = "http://www.compbio.dundee.ac.uk/jpred4/cgi-bin/rest"
    FAILED_ID = 'jp_fail'

    def submit(self, cmd, cwd):
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
            return job_id
        except AttributeError:
            return self.FAILED_ID

    @classmethod
    def check_status(cls, job_id, cwd) -> JobStatus:
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
            archive.extractall(cwd)
        return JobStatus.COMPLETED
