from distutils.core import setup

setup(
    name='myvagrant',
    version='0.1',
    packages=['', 'myvagrant'],
    entry_points={
        'console_scripts':
            ['myvagrant = myvagrant.shell:vagrant', 'myvagrant-config = myvagrant.shell:config']
    },
    install_requires=[
        'PyYAML'
    ],
    url='https://github.com/suhanovv/myvagrant',
    license='',
    author='suhanovv',
    author_email='vadimsuhanov@gmao;.com',
    description=''
)
