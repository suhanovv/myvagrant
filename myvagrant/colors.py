class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

def blue(text):
    return '%s %s %s' % (bcolors.OKBLUE, text, bcolors.ENDC)

def green(text):
    return '%s %s %s' % (bcolors.OKGREEN, text, bcolors.ENDC)

def red(text):
    return '%s %s %s' % (bcolors.FAIL, text, bcolors.ENDC)

def yellow(text):
    return '%s %s %s' % (bcolors.WARNING, text, bcolors.ENDC)
