
import sys
import icfp_api
import json
import io
from functools import reduce


def read_solution(f):
    with io.open(f['fname'], 'r') as h:
        sol = json.loads(h.read())
        if sol.__class__.__name__ != 'list':
            sys.exit(1)
        for p in sol:
            if p.__class__.__name__ != 'dict':
                sys.exit(1)
            p['pantag'] = f['tag']
        return sol


def is_valid_solution(sol):
    if (sol.__class__.__name__ != 'list') or (sol == []):
        return False

    p = sol[0]

    if ('pscore' not in p) or (p['pscore'].__class__.__name__ != 'int'):
        return False
    if ('seed' not in p) or (p['seed'].__class__.__name__ != 'int'):
        return False
    if ('problemId' not in p) or (p['problemId'].__class__.__name__ != 'int'):
        return False
    if ('solution' not in p) or (p['solution'].__class__.__name__ != 'str'):
        return False
    if ('tag' not in p) or (p['tag'].__class__.__name__ != 'str'):
        return False

    return True


def merge_problems(p1, p2):
    if p1['seed'] != p2['seed']:
        print('seeds differ(%d): %s(%d) <> %s(%d)' %
              ((p1['problemId']),
               (p1['pantag']),
               (p1['seed']),
               (p2['pantag']),
               (p2['seed'])))
        return p2
    if (not 'score' in p1) or (not 'pscore' in p1):
        print('has no score: %s' % (p1['pantag']))
        return p2
    if (not 'score' in p2) or (not 'pscore' in p2):
        print('has no score: %s' % (p2['pantag']))
        return p1

    s1 = p1['score'] + p1['pscore']
    s2 = p2['score'] + p2['pscore']
    if s1 > s2:
        return p1
    else:
        return p2


def compose_panopticum(tag):
    filtered = icfp_api.filter_solutions(None)
    filtered = [ f for f in filtered if 'panopticum' not in f['tag']]
    # filtered = [ f for f in filtered if 'fixed-potential' not in f['tag']  ]
    solutions = [ read_solution(f) for f in filtered ]
    solutions = [ sol for sol in solutions if is_valid_solution(sol) ]

    pid_groups = {}
    for sol in solutions:
        pid = sol[0]['problemId']
        if pid in pid_groups:
            pid_groups[pid].append(sol)
        else:
            pid_groups[pid] = [ sol ]

    for pid, group in pid_groups.items():

        def merge_solutions(sol1, sol2):
            if len(sol1) > len(sol2):
                print('lengths do not match: %d' % pid)
                return sol1
            if len(sol1) < len(sol2):
                print('lengths do not match: %d' % pid)
                return sol2
            return [ merge_problems(p1, p2) for (p1, p2) in zip(sol1, sol2) ]

        s1 = group[0]
        for s2 in group:
            s1 = merge_solutions(s1, s2)

        for p in s1:
            p['tag'] = tag
        fname = '../../data/solutions/solution_%d_%s.json' % (pid, tag)
        with io.open(fname, 'w') as h:
            h.write(json.dumps(s1))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: panopticum.py tag')
        sys.exit(1)
    compose_panopticum(sys.argv[1])
