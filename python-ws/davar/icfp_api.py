
import subprocess
import sys
import re
import io
import time
import main as mm
from os import listdir


team_id = 42
team_token = ":C0x3lXwXH12jFaTOA1LEKRHycE9aeXAsaAmm8UPFlPE="


def send_solution(fname) -> bool:
    print('Sending %s...' % fname)
    res = subprocess.call(
        ["curl",
         "--user", team_token,
         "-X", "POST",
         "-H", "Content-Type: application/json",
         "--data", '@' + fname,
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
    return { 'set_id': int(m.group('set_id')),
             'solver': m.group('solver'),
             'version': int(m.group('version')) }


def filter_solutions(solver, version):
    files = [ ('../../solutions/' + f, parse_solution_fname(f))
              for f in listdir("../../solutions") ]

    def is_requested(info):
        return ((info['solver'] == solver) and (info['version'] == version))

    files = [ (f, i) for (f, i) in files if is_requested(i) ]
    files.sort(key = lambda pair: pair[1]['set_id'])
    return files


def send_all_solutions(solver, version):
    filtered = filter_solutions(solver, version)
    for f, info in filtered:
        time.sleep(1)
        if not send_solution(f):
            return


def score_solution(fname, info, log):
    scores0 = mm.getScore(fname)
    scores, pscores = zip(*scores0)
    msg = 'Id = %d %d %d %s' % (info['set_id'],
                                sum(scores) // len(scores),
                                sum(pscores) // len(pscores),
                                scores0)
    print(msg)
    log.write(msg + '\n')
    return (scores, pscores)


def score_all_solutions(solver, version):
    filtered = filter_solutions(solver, version)
    total = 0
    totalp = 0
    with io.open('log_%s_%d.txt' % (solver, version), 'w') as log:
        for (f, info) in filtered:
            (scores, pscores) = score_solution(f, info, log)
            total += sum(scores) / len(scores)
            totalp += sum(pscores) / len(pscores)
        msg = 'Total = %.2f (%.2f + %.2f)' % (total + totalp, total, totalp)
        print(msg)
        log.write(msg + '\n')


def compare_solutions(solver, version1, version2):
    files = zip(filter_solutions(solver, version1), filter_solutions(solver, version2))
    total = 0
    with io.open('log_%s_%d-%d.txt' % (solver, version1, version2), 'w') as log:
        for (f1, info1), (f2, info2) in files:
            assert(info1['set_id'] == info2['set_id'])
            scores1 = mm.getScore(f1)
            scores2 = mm.getScore(f2)
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
