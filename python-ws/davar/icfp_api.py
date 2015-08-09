
import subprocess
import sys
import re
import io
import time
import json
import main as mm
from os import listdir


team_id = 42
team_token = ":C0x3lXwXH12jFaTOA1LEKRHycE9aeXAsaAmm8UPFlPE="


def sanitize_problem(p):
    sanitized = {}
    sanitized['problemId'] = p['problemId']
    sanitized['seed'] = p['seed']
    sanitized['solution'] = p['solution']
    sanitized['tag'] = p['tag']
    return sanitized


def write_sanitized_solution(f):
    tempFile = '../../temp.json'

    with io.open(f['fname'], 'r') as h:
        sol = json.loads(h.read())
    with io.open(tempFile, 'w') as h:
        tempSol = [ sanitize_problem(p) for p in sol ]
        h.write(json.dumps(tempSol))

    return tempFile


def send_solution(f) -> bool:
    tempFile = write_sanitized_solution(f)
    print('Sending %s...' % f['fname'])
    res = subprocess.call(
        ["curl",
         "--user", team_token,
         "-X", "POST",
         "-H", "Content-Type: application/json",
         "--data", '@' + tempFile,
         "https://davar.icfpcontest.org/teams/%s/solutions" % team_id ])
    print()
    return (res == 0)


def get_results() -> bool:
    res = subprocess.call(
        ["curl",
         "--user", team_token,
         "-X", "GET",
         "https://davar.icfpcontest.org/teams/%s/solutions" % team_id ])
    print()
    return (res == 0)


solution_name_rx = re.compile('solution_'
                              '(?P<set_id>[0-9]+)_'
                              '(?P<solver>[a-z]+)_'
                              '(?P<version>[0-9]+)')

def parse_solution_fname(fname):
    m = re.match(solution_name_rx, fname)
    return { 'fname': '../../solutions/' + fname,
             'set_id': int(m.group('set_id')),
             'solver': m.group('solver'),
             'version': int(m.group('version')) }


def filter_solutions(solver, version):
    files = [ parse_solution_fname(f) for f in listdir("../../solutions") ]

    def is_requested(f):
        return ((f['solver'] == solver) and (f['version'] == version))

    files = [ f for f in files if is_requested(f) ]
    files.sort(key = lambda f: f['set_id'])
    return files


def send_all_solutions(solver, version):
    filtered = filter_solutions(solver, version)
    for f in filtered:
        time.sleep(1)
        if not send_solution(f):
            return


def score_solution(f, log):
    scores0 = mm.getScore(f['fname'])
    scores, pscores = zip(*scores0)
    msg = 'Id = %d %d %d %s' % (f['set_id'],
                                sum(scores) // len(scores),
                                sum(pscores) // len(pscores),
                                scores0)
    print(msg)
    log.write(msg + '\n')
    return (scores, pscores)


def score_all_solutions_internal(solver, version, action):
    filtered = filter_solutions(solver, version)
    total = 0
    totalp = 0
    with io.open('log_%s_%d.txt' % (solver, version), 'w') as log:
        for f in filtered:
            (scores, pscores) = score_solution(f, log)
            action(f, scores, pscores)
            total += sum(scores) / len(scores)
            totalp += sum(pscores) / len(pscores)
        msg = 'Total = %.2f (%.2f + %.2f)' % (total + totalp, total, totalp)
        print(msg)
        log.write(msg + '\n')


def score_all_solutions(solver, version):
    def action(*args, **kargs):
        return None
    score_all_solutions_internal(solver, version, action)


def score_and_mark_all_solutions(solver, version):
    def action(f, scores, pscores):
        with io.open(f['fname'], 'r') as h:
            sol = json.loads(h.read())
        with io.open(f['fname'], 'w') as h:
            for i, v in enumerate(scores):
                sol[i]['score'] = scores[i]
                sol[i]['pscore'] = pscores[i]
            h.write(json.dumps(sol))
    score_all_solutions_internal(solver, version, action)


def compare_solutions(solver, version1, version2):
    files = zip(filter_solutions(solver, version1), filter_solutions(solver, version2))
    total = 0
    with io.open('log_%s_%d-%d.txt' % (solver, version1, version2), 'w') as log:
        for f1, f2 in files:
            assert(f1['set_id'] == info2['set_id'])
            scores1 = mm.getScore(f1['fname'])
            scores2 = mm.getScore(f2['fname'])
            assert(len(scores1) == len(scores2))
            diff = sum(scores2) - sum(scores1)
            diffa = [b - a for a, b in zip(scores1, scores2)]

            msg = 'Id = %d %.0f %s' % (id1, diff / len(scores1), diffa)
            print(msg)
            log.write(msg + '\n')
            total += diff / len(scores1)
        msg = 'Total diff = %.2f' % total
        print(msg)
        log.write(msg + '\n')


def main():
    send_all_solutions(sys.argv[1], int(sys.argv[2]))


if __name__ == '__main__':
    main()
