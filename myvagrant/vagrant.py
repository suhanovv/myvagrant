from Queue import Queue
import os
import shutil
import subprocess
import sys
import re
from threading import Thread

from myvagrant.config import Config, Credentials
from myvagrant.colors import blue, green, red, yellow
from myvagrant.utils import is_python_project


class Vagrant(object):

    def __init__(self):
        self.config = Config().load()
        self._vms = None

    def _run_command(self, *args, **kwargs):

        command = ['vagrant'] + [arg for arg in args if arg is not None]

        cwd = os.path.abspath(kwargs.get('cwd', None) or os.getcwd())

        if kwargs.get('silent_err', False):
            stderr = open(os.devnull, 'wb')
        else:
            stderr = sys.stderr

        if not kwargs.get('capture_output', False):
            retval = subprocess.check_call(command, cwd=cwd, stderr=stderr)
        else:
            retval = subprocess.check_output(command, cwd=cwd, stderr=stderr)

        if kwargs.get('silent_err', False):
            stderr.close()

        return retval

    def _get_vms(self):
        projects_path = self.config.get('projects_dir')

        if not self._vms:

            def is_valid(path_name, dir_name):
                _path = os.path.join(path_name, dir_name)
                if os.path.isdir(_path) and not dir_name.startswith('.') and os.path.exists(
                        os.path.join(_path, 'Vagrantfile')):
                    return True
                return False
            self._vms = {item: os.path.join(projects_path, item) for item in os.listdir(projects_path) if
                        is_valid(projects_path, item)}
        return self._vms


    def _get_reserved_ips(self):
        ips = []

        def parse_vagrantfile(file_path):
            template = re.compile('ip: \"(?P<ip>192.168.\d{1,3}.\d{1,3})\"')
            with open(file_path) as fp:
                for line in fp.readlines():
                    if not line.strip().startswith('#'):
                        try:
                            return template.search(line).group('ip')
                        except:
                            pass


        for project in self._get_vms().values():
            ip = parse_vagrantfile(os.path.join(project, 'Vagrantfile'))
            if ip:
                ips.append(ip)
        return sorted(ips)

    def _get_new_ip(self):
        part_1, part_2, part_3, part_4 = self.config.get('ip_range').split('.')
        tmp_part_3 = map(lambda x: int(x), part_3.split('/'))
        tmp_part_4 = map(lambda x: int(x), part_4.split('/'))
        for item_3 in xrange(*tmp_part_3):
            for item_4 in xrange(*tmp_part_4):
                test_ip = '.'.join([part_1, part_2, str(item_3), str(item_4)])
                if test_ip not in self._get_reserved_ips():
                    return test_ip

        raise BaseException('All ips are reserved')

    def _get_project_status(self, name):
        try:
            info = self._run_command('status', cwd=self._get_vms().get(name), silent_err=True, capture_output=True)
            if 'poweroff' in info:
                return {'name': name, 'status': 'poweroff'}
            elif 'running' in info:
                return {'name': name, 'status': 'running'}
            else:
                return {'name': name, 'status': '?'}
        except BaseException:
            return {'name': name, 'status': '?'}

    def _get_projects_status(self, names=None):
        projects = {}
        vms = self._get_vms()
        if names is not None:
            for name in names:
                project = vms.get(name, None)
                if project:
                    projects[name] = project
        else:
            projects = vms

        statuses = []
        queue = Queue()

        get_status = self._get_project_status

        def worker():
            while not queue.empty():
                item = queue.get()
                statuses.append(get_status(item))
                queue.task_done()


        for project in projects.keys():
            queue.put(project)

        for i in xrange(5):
            t = Thread(target=worker)
            t.daemon = True
            t.start()

        queue.join()
        statuses.sort(key=lambda x: (x['status'], x['name']), reverse=True)

        return statuses

    def _get_colored_status(self, status):
        if status == 'poweroff':
            return blue(status)
        elif status == 'running':
            return green(status)
        else:
            return yellow(status)

    def _create_project(self, name, box_name=None, with_api=None):
        project_dir = os.path.join(self.config.get('projects_dir'), name)
        for item in ['repo',]:
            dirname = os.path.join(project_dir, item)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
                print green("==> Dir created: %s" % dirname)

        vagrant_tpl = self.config.get('vagrant_tpl')
        vagrant_proj = os.path.join(project_dir, 'Vagrantfile')

        if not os.path.exists(vagrant_proj):
            shutil.copy(vagrant_tpl, vagrant_proj)
            with open(vagrant_tpl) as tpl_fp:
                tpl_lines = tpl_fp.read()
                with open(vagrant_proj, 'w+') as fp:
                    tpl_lines = tpl_lines.replace('{IP}', self._get_new_ip())
                    tpl_lines = tpl_lines.replace('{BOX_NAME}', box_name or self.config.get('box_name'))
                    tpl_lines = tpl_lines.replace('{HOST_NAME}', name)
                    tpl_lines = tpl_lines.replace('{PROJECT_DIR}', project_dir)
                    tpl_lines = tpl_lines.replace('{CREDENTIALS}', Credentials().filename)
                    tpl_lines = tpl_lines.replace('{ENVIRONMENT}', 'python' if is_python_project(name) else 'php')
                    tpl_lines = tpl_lines.replace('{IS_API}', 'true' if with_api else 'false')
                    fp.seek(0)
                    fp.write(tpl_lines)
                    fp.truncate()
            print green("==> Vagrantfile created: %s" % vagrant_proj)

        shutil.copytree(os.path.join(Config().path, 'provisions/provision'), os.path.join(project_dir, 'provision'))


    def init(self, *args, **kwargs):
        if len(args) == 0:
            command = ['init', kwargs.get('box_name', None), kwargs.get('box_url', None)]
            self._run_command(*command)
            return
        for name in args:
            self._create_project(name, kwargs.get('box_name', None), kwargs.get('with_api', None))


    def halt(self, *args, **kwargs):
        if len(args) == 0:
            self._run_command('halt')
            return

        if 'all' in args:
            args = self._get_vms().keys()

        for name in args:
            self._run_command('halt', cwd=self._get_vms().get(name))

    def up(self, *args, **kwargs):
        if len(args) == 0:
            self._run_command('up')
            return

        for name in args:
            self._run_command('up', cwd=self._get_vms().get(name))


    def suspend(self, *args, **kwargs):
        pass

    def ssh(self, *args, **kwargs):
        self._run_command('ssh', cwd=self._get_vms().get(args[0]) if len(args) > 0 else None)


    def destroy(self, *args, **kwargs):
        if len(args) == 0:
            self._run_command('destroy')
            return
        for name in args:
            path = os.path.join(self.config.get('projects_dir'), name)
            self._run_command('destroy', '-f', cwd=path)
            shutil.rmtree(path)
            print red("==> Dir deleted: %s" % path)


    def list(self, *args, **kwargs):
        projects = self._get_vms()
        print '\n'.join(projects)

    def status(self, *args, **kwargs):
        if len(args) == 0:
            self._run_command('status')
            return
        elif len(args) == 1 and 'all' not in args:
            projects = [self._get_project_status(*args)]
        else:
            if 'all' in args:
                args = None
            projects = self._get_projects_status(names=args)
        projects = ["%s - %s" % (item.get('name'), self._get_colored_status(item.get('status'))) for item in projects]

        print '\n'.join(projects)

