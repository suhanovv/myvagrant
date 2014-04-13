import os
import yaml


class Config(object):
    def __init__(self, config_path=None, config_file='config.yml'):
        if not config_path:
            config_path = os.path.join(os.path.expanduser('~'), '.myvagrant')
        self.root_path = config_path
        self.filename = os.path.join(config_path, config_file)
        self.data = {}

    def load(self):
        stream = file(self.filename, 'r')
        self.data = yaml.load(stream)
        return self.data


    def save(self, **kwargs):
        self.data.update(kwargs)
        if not os.path.exists(os.path.dirname(self.filename)):
            os.makedirs(os.path.dirname(self.filename))
        stream = file(self.filename, 'w')
        yaml.dump(self.data, stream, default_flow_style=False, explicit_start=True)

    @property
    def file(self):
        return self.filename

    @property
    def path(self):
        return self.root_path


class Credentials(Config):

    def __init__(self, config_path=None):
        super(Credentials, self).__init__(config_path, 'credentials/credentials.yml')