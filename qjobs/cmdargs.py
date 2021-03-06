"""parses command arguments"""

import argparse


def add_args(parser, defaults):
    """add mains arguments and defaults to parser"""

    parser = argparse.ArgumentParser(parents=[parser])
    parser.add_argument('-i', '--items', action='store_true',
                        help='display descriptions of items and exit')
    parser.add_argument('-r', '--reverse', action='store_true',
                        help='total before out')
    parser.add_argument('-o', '--out', nargs='?', const='', metavar='ITEMS',
                        help='specify which items are displayed')
    parser.add_argument('-O', '--out_format',
                        nargs='?', const='', metavar='FMT',
                        help='specify format of job list output')
    parser.add_argument('-t', '--total', nargs='?', const='', metavar='ITEMS',
                        help='specify items for which you want \
                                to count the jobs')
    parser.add_argument('-s', '--sort', metavar='ITEMS',
                        help='specify the items to use to sort the jobs')
    parser.add_argument('--elapsed_format', metavar='FMT',
                        help='specify e item format')
    parser.add_argument('-u', '--users', nargs='?', const='*',
                        metavar='USR1,USR2,...',
                        help='specify list of users, use commas \
                            to separate usernames, empty list \
                            will list jobs of all users')
    parser.add_argument('-f', '--file', type=argparse.FileType('r'),
                        help='use given xml file as input (for debug)')
    parser.add_argument('--sep',
                        help='separator between `out` columns')
    parser.add_argument('--width_tot', type=int, metavar='INT',
                        help='max width for `total` columns')
    parser.add_argument('--sep_tot',
                        help='separator between `total` columns')
    parser.add_argument('--mute', action='store_true',
                        help='no output if no jobs')
    parser.add_argument('-e', '--edit_config', action='store_true',
                        help='edit config file with text editor')
    parser.add_argument('-E', '--edit_interactive', action='store_true',
                        help='edit config file in an interactive way')

    parser.set_defaults(**defaults)
    return parser


def parse():
    """parse arguments given in command line and fetch
    default config from config file."""

    import shlex
    from subprocess import call
    import sys

    from . import configfile, constants
    from .misc import itmfilter, rm_brackets

    parser = argparse.ArgumentParser(
        description='qstat wrapper for better output. \
            Available ITEMS are "' + ''.join(constants.itms.keys()) +
        '" see -i option for their description.', add_help=False)
    parser.add_argument('-c', '--config',
                        nargs='?',
                        const=None,
                        default=constants.path_config,
                        metavar='FILE',
                        help='specify config file, write current config \
                              if called without argument')
    parser.add_argument('--default_config', action='store_true',
                        help='config file set to default config')

    args, remaining_argv = parser.parse_known_args()

    if args.default_config:
        configfile.write(constants.default_config, constants.path_config)
        sys.exit()

    config_to_stdout = not args.config

    parser = add_args(parser, configfile.read(args))
    args = parser.parse_args(remaining_argv)

    args.out = itmfilter(args.out)
    args.total = itmfilter(args.total, True)
    args.sort = itmfilter(args.sort)

    if config_to_stdout:
        configfile.write(vars(args), sys.stdout)
        sys.exit()

    if args.edit_config:
        call(shlex.split(args.editor + ' ' + constants.path_config))
        sys.exit()

    if args.edit_interactive:
        return args

    args.sep = rm_brackets(args.sep)
    args.sep_tot = rm_brackets(args.sep_tot)

    args.start_format = args.start_format.replace('{', '%').replace('}', '')
    if not args.out_format:
        args.out_format = args.sep.join('{{' + itm + ':{' + itm + '}}}'
                                        for itm in args.out)

    return args
