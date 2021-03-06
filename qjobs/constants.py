"""defines constants for qjobs"""

import getpass
from collections import OrderedDict, namedtuple
from os.path import expanduser

Itmtp = namedtuple('Itmtp', ['dscr', 'xml_tag'])

itms = OrderedDict((
    ('i', Itmtp('job id', ['JB_job_number'])),
    ('p', Itmtp('job priority', ['JAT_prio'])),
    ('n', Itmtp('job name', ['JB_name'])),
    ('o', Itmtp('job owner', ['JB_owner'])),
    ('s', Itmtp('job state', ['state'])),
    ('t', Itmtp('job start/submission time', ['JAT_start_time',
                                              'JB_submission_time'])),
    ('e', Itmtp('elapsed time since start/submission', [])),
    ('q', Itmtp('queue name without domain', [])),
    ('d', Itmtp('queue domain', [])),
    ('k', Itmtp('queue name with domain', ['queue_name'])),
    ('r', Itmtp('requested queue(s)', ['hard_req_queue'])),
    ('l', Itmtp('number of slots used', ['slots']))
    ))

path_config = '~/.config/qjobs/config'
path_config = expanduser(path_config)

dflt_section = 'Defaults'

default_config = OrderedDict((
    ('out', 'instq'),
    ('total', 's'),
    ('sort', 'ips'),
    ('reversed_itms', 'psl'),
    ('out_format', ''),
    ('start_format', '{Y}-{m}-{d} {H}:{M}:{S}'),
    ('elapsed_format', '{H:03d}:{m:02d} ({D:.2f} days)'),
    ('width_tot', 120),
    ('sep_tot', '[     ]'),
    ('sep', '[   ]'),
    ('users', getpass.getuser()),
    ('editor', 'vim'),
    ('qstat_cmd', 'qstat')
    ))
