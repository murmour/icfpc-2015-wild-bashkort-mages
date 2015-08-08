
import subprocess
import sys
import re
import io
import time
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

    return [ f for f in listdir("../../solutions") if is_requested(f) ]


def send_all_solutions(solver, version):
    filtered = filter_solutions(solver, version)
    for f in filtered:
        time.sleep(1)
        if not send_solution('../../solutions/' + f):
            return


if __name__ == '__main__':
    send_all_solutions(sys.argv[1], int(sys.argv[2]))
