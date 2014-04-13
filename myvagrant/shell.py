# coding=utf-8
import argparse
from myvagrant.vagrant import Vagrant
from myvagrant.utils import check_first_run



def vagrant():
    check_first_run()
    vagrant = Vagrant()

    project_parser = argparse.ArgumentParser(description='Vagrant Ailove wrapper')
    action_subparser = project_parser.add_subparsers()
    project_init_parser = action_subparser.add_parser('init', help='Create project')
    project_init_parser.add_argument('name', nargs='*', help='Projects name', default=[])
    project_init_parser.add_argument('--box-name', '-bn', nargs='?', help='Box name')
    project_init_parser.add_argument('--box-url', '-bu', nargs='?', help='Box url')
    project_init_parser.add_argument('--with-api', nargs='?', help='With api settings')
    project_init_parser.set_defaults(action=vagrant.init)

    project_up_parser = action_subparser.add_parser('up', help='Run project')
    project_up_parser.add_argument('name', nargs='*', help='Projects name', default=[])
    project_up_parser.set_defaults(action=vagrant.up)

    project_halt_parser = action_subparser.add_parser('halt', help='Power off project')
    project_halt_parser.add_argument('name', nargs='*', help='Projects name', default=[])
    project_halt_parser.set_defaults(action=vagrant.halt)

    project_halt_parser = action_subparser.add_parser('ssh', help='Ssh to project')
    project_halt_parser.add_argument('name', nargs='?', help='Projects name', default=[])
    project_halt_parser.set_defaults(action=vagrant.ssh)

    project_halt_parser = action_subparser.add_parser('destroy', help='Destroy project')
    project_halt_parser.add_argument('name', nargs='*', help='Projects name', default=[])
    project_halt_parser.set_defaults(action=vagrant.destroy)

    project_list_parser = action_subparser.add_parser('list', help='Run project')
    project_list_parser.set_defaults(action=vagrant.list)

    project_status_parser = action_subparser.add_parser('status', help='Get status project VM')
    project_status_parser.add_argument('name', nargs='*', help='Project name or "all"', default=[])
    project_status_parser.set_defaults(action=vagrant.status)

    project_parser.set_defaults(cls=Vagrant)

    args = project_parser.parse_args()
    if 'name' in args:
        if isinstance(args.name, str):
            args.name = [args.name]
        args.action(*args.name, **vars(args))
    else:
        args.action(**vars(args))


def config():
    print 'config'