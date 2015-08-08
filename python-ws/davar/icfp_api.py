
import subprocess
import sys
import re
import io
import time
import main as mm
from os import listdir


team_id = 42
team_token = ":C0x3lXwXH12jFaTOA1LEKRHycE9aeXAsaAmm8UPFlPE="


def send_solution(filename) -> bool:
    res = subprocess.call(
        ["curl",
         "--user", team_token,
         "-X", "POST",
         "-H", "Content-Type: application/json",
         "--data", '@' + filename,
         "https://davar.icfpcontest.org/teams/%s/solutions" % team_id ])

    print()
    return (res == 0)


def filter_solutions(solver, version):
    rx = re.compile('solution_'
                    '(?P<set_id>[0-9]+)_'
                    '(?P<solver>[a-z]+)_'
                    '(?P<version>[0-9]+)')

    def is_requested(f):
        m = re.match(rx, f)
        return ((m.group('solver') == solver) and
                (int(m.group('version')) == version))

    return [ '../../solutions/' + f for f in listdir("../../solutions") if is_requested(f) ]


def send_all_solutions(solver, version):
    filtered = filter_solutions(solver, version)
    for f in filtered:
        time.sleep(1)
        if not send_solution(f):
            return


def score_all_solutions(solver, version):
    filtered = filter_solutions(solver, version)
    total = 0
    with io.open('log_%s_%d.txt' % (solver, version), 'w') as log:
        for f in filtered:
            scores = mm.getScore(f)
            msg = '%s %d %s' % (f, sum(scores), scores)
            print(msg)
            log.write(msg + '\n')
            total += sum(scores) / len(scores)
        msg = 'Total = %.2f' % total
        print(msg)
        log.write(msg + '\n')
    
    
def main():
    score_all_solutions('rip', 2)
    #send_all_solutions(sys.argv[1], int(sys.argv[2]))
    
if __name__ == '__main__':
    main()
    
