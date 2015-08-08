
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

    def get_id(f):
        m = re.match(rx, f)
        return int(m.group('set_id'))
    
    def is_requested(f):
        m = re.match(rx, f)
        return ((m.group('solver') == solver) and
                (int(m.group('version')) == version))    

    files = [ f for f in listdir("../../solutions") if is_requested(f) ]
    files.sort(key = lambda x: get_id(x))
    return [ ('../../solutions/' + f, get_id(f)) for f in files ]


def send_all_solutions(solver, version):
    filtered = filter_solutions(solver, version)
    for f, _id in filtered:
        time.sleep(1)
        print('Sending %s...' % f)
        if not send_solution(f):
            return


def score_all_solutions(solver, version):
    filtered = filter_solutions(solver, version)
    total = 0
    with io.open('log_%s_%d.txt' % (solver, version), 'w') as log:
        for f, ident in filtered:
            scores = mm.getScore(f)
            msg = 'Id = %d %d %s' % (ident, sum(scores), scores)
            print(msg)
            log.write(msg + '\n')
            total += sum(scores) / len(scores)
        msg = 'Total = %.2f' % total
        print(msg)
        log.write(msg + '\n')
    
def compare_solutions(solver, version1, version2):
    files = zip(filter_solutions(solver, version1), filter_solutions(solver, version2))
    total = 0
    with io.open('log_%s_%d-%d.txt' % (solver, version1, version2), 'w') as log:
        for (f1, id1), (f2, id2) in files:
            assert(id1 == id2)
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
    #score_all_solutions('rip', 4)
    compare_solutions('rip', 2, 4)
    #send_all_solutions(sys.argv[1], int(sys.argv[2]))
    
if __name__ == '__main__':
    main()
    
