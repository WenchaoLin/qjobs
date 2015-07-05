#!PYTHON_CMD
from configparser import ConfigParser as CP

items = 'ipnostqdQl'
items_description = [
        ('i', 'job id'),
        ('p', 'job priority'),
        ('n', 'job name'),
        ('o', 'job owner'),
        ('s', 'job state'),
        ('t', 'job start/submission time'),
        ('q', 'queue name without domain'),
        ('d', 'queue domain'),
        ('Q', 'queue name with domain'),
        ('l', 'number of slots used')]
default_config = {
        'out': 'instq',
        'total': 's',
        'sort': 'ips',
        'width_tot': 120,
        'sep_tot': 5,
        'sep': 3,
        'users': 'USER_NAME'}
reversed_items = 'psl'


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(
            description='qstat wrapper for better output. \
            Available ITEMS are "' + items +
            '" see -i option for their description.', add_help=False)
    parser.add_argument('-c', '--config',
                        default='PATH_CONFIG',
                        metavar='FILE',
                        help='specify config file')

    args, remaining_argv = parser.parse_known_args()
    try:
        conf_parser = CP()
        conf_parser.read(args.config)
        defaults = dict(conf_parser.items('Defaults'))
    except:
        print('Cannot read config file, run install.sh script')
        defaults = default_config

    parser = argparse.ArgumentParser(parents=[parser])
    parser.add_argument('-i', '--items', action='store_true',
                        help='display descriptions of items and exit')
    parser.add_argument('-o', '--out', nargs='?', const='', metavar='ITEMS',
                        help='specify which items are displayed.')
    parser.add_argument('-t', '--total', nargs='?', const='', metavar='ITEMS',
                        help='specify items for which you want \
                                to count the jobs.')
    parser.add_argument('-s', '--sort', metavar='ITEMS',
                        help='specify the items to use to sort the jobs')
    parser.add_argument('-u', '--users', nargs='?', const='*',
                        metavar='USR1,USR2,...',
                        help='specify list of users, use commas \
                            to separate usernames, empty list \
                            will list jobs of all users')
    parser.add_argument('-f', '--file', type=argparse.FileType('r'),
                        help='use given xml file as input (for debug)')
    parser.add_argument('--sep', type=int, metavar='INT',
                        help='number of spaces between `out` columns')
    parser.add_argument('--width_tot', type=int, metavar='INT',
                        help='max width for `total` columns')
    parser.add_argument('--sep_tot', type=int, metavar='INT',
                        help='number of spaces between `total` columns')

    parser.set_defaults(**defaults)
    args = parser.parse_args(remaining_argv)
    return args


def main():
    from itertools import zip_longest as ziplgst
    from math import ceil
    from subprocess import Popen, PIPE
    import sys
    import xml.etree.ElementTree as ET

    args = parse_args()
    if args.items:
        print(*('{}: {}'.format(k, v) for k, v in items_description),
              sep='\n')
        sys.exit()

    if args.file:
        f = args.file
    else:
        f = Popen('\qstat -u "' + args.users + '" -xml -r',
                  shell=True, stdout=PIPE).stdout

    columns = ''
    for c in args.out:
        if c in items:
            columns += c

    totals = ''
    for c in args.total:
        if c.lower() in items:
            totals += c

    jobsTree = ET.parse(f)
    jobsList = jobsTree.getroot().iter('job_list')

    alljobs = []
    jobCounts = {}

    for j in jobsList:
        job = {}
        job['i'] = j.find('JB_job_number').text
        job['p'] = j.find('JAT_prio').text
        job['n'] = j.find('JB_name').text
        job['o'] = j.find('JB_owner').text
        job['s'] = j.find('state').text
        job['q'] = ''
        job['d'] = ''
        job['Q'] = ''
        job['l'] = j.find('slots').text
        if job['s'] == 'r':
            job['t'] = j.find('JAT_start_time').text
            job['Q'] = j.find('queue_name').text
            job['q'], job['d'] = job['Q'].rsplit('@')
        elif job['s'] in ['dt', 'dr']:
            job['t'] = j.find('JAT_start_time').text
        else:
            try:
                job['t'] = j.find('JB_submission_time').text
            except AttributeError:
                job['t'] = None
        if job['t']:
            job['t'] = job['t'].replace('T', ' ')
        else:
            job['t'] = 'not set'

        for c in totals.lower():
            if c not in jobCounts:
                jobCounts[c] = {}
            if job[c] in jobCounts[c]:
                jobCounts[c][job[c]] += 1
            else:
                jobCounts[c][job[c]] = 1

        alljobs.append(job)

    if not alljobs:
        print('No pending or running job.')
    else:
        if columns:
            for c in args.sort:
                if c in items:
                    alljobs.sort(key=lambda job: job[c],
                                 reverse=(c in reversed_items))
            l = {}
            for c in columns:
                l[c] = max(len(job[c]) for job in alljobs)

            for job in alljobs:
                print(*(job[c].ljust(l[c]) for c in columns),
                      sep=' '*args.sep)
            if totals:
                print()

        if totals:
            print('tot: {}'.format(len(alljobs)))
            for c in totals:
                order_by_keys = 0
                if c.isupper():
                    order_by_keys = 1
                    c = c.lower()
                dc = jobCounts[c]
                if '' in dc:
                    dc['not set'] = dc.pop('')
                dc = sorted(dc.items(),
                            key=lambda x: x[order_by_keys],
                            reverse=(c in reversed_items) or order_by_keys)
                lk = max(len(k) for k, _ in dc)
                lv = max(len(str(v)) for _, v in dc)
                sp = ' '*args.sep_tot
                wd = args.width_tot
                nf = (wd+len(sp))//(lk+lv+2+len(sp))
                if nf == 0:
                    nf = 1

                dc = ziplgst(*(iter(dc), ) * int(ceil(len(dc)/nf)),
                             fillvalue=(None, None))
                dc = zip(*dc)

                print()
                for line in dc:
                    print(*('{}: {}'.format(k.ljust(lk), str(v).rjust(lv))
                          for k, v in line if (k, v) != (None, None)),
                          sep=sp)

if __name__ == '__main__':
    main()
