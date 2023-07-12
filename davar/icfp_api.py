
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


def sanitize_solution(sol):
    return [ sanitize_problem(p) for p in sol ]


def write_sanitized_solution(fname):
    tempFile = '../../temp.json'

    with io.open(fname, 'r') as h:
        sol = json.loads(h.read())
    with io.open(tempFile, 'w') as h:
        tempSol = sanitize_solution(sol)
        h.write(json.dumps(tempSol))

    return tempFile


def send_solution(fname) -> bool:
    tempFile = write_sanitized_solution(fname)
    print('Sending %s...' % fname)
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
                              r'(?P<tag>[a-z0-9\-]+)_'
                              '(?P<version>[0-9]+).json')

def parse_solution_fname(fname):
    m = re.match(solution_name_rx, fname)
    return { 'fname': '../../data/solutions/' + fname,
             'set_id': int(m.group('set_id')),
             'tag': '%s_%s' % (m.group('tag'), m.group('version')) }


problem_name_rx = re.compile('problem_(?P<id>[0-9]+).json')

def parse_problem_fname(fname):
    m = re.match(problem_name_rx, fname)
    return { 'fname': '../../data/problems/' + fname,
             'id': int(m.group('id')) }


def filter_problems(lowIndex, highIndex):
    files = [ parse_problem_fname(f) for f in listdir("../../data/problems") ]

    def is_requested(f):
        return ((f['id'] >= lowIndex) and (f['id'] <= highIndex))

    files = [ f for f in files if is_requested(f) ]
    files.sort(key = lambda f: f['id'])
    return files


def filter_solutions(tag):
    files = [ parse_solution_fname(f) for f in listdir("../../data/solutions") ]
    files = [ f for f in files if (tag == None or f['tag'] == tag) ]
    files.sort(key = lambda f: f['set_id'])
    return files


def send_all_solutions(tag):
    filtered = filter_solutions(tag)
    for f in filtered:
        time.sleep(1)
        if not send_solution(f['fname']):
            return


def score_solution(f, log):
    scores0 = mm.getScore(f['fname'])
    scores, pscores = zip(*scores0)
    avgScore = sum(scores) // len(scores)
    avgPScore = sum(pscores) // len(pscores)
    avgTotal = (sum(scores) + sum(pscores)) // len(pscores)
    msg = 'Id = %d, score = %d (%d + %d)' % (f['set_id'],
                                             avgTotal,
                                             avgScore,
                                             avgPScore)
    print(msg)
    print(scores0)
    log.write(msg + '\n')
    return (scores, pscores)


def score_all_solutions_internal(tag, action):
    filtered = filter_solutions(tag)
    total = 0
    totalp = 0
    with io.open('log_%s.txt' % tag, 'w') as log:
        for f in filtered:
            (scores, pscores) = score_solution(f, log)
            action(f, scores, pscores)
            total += sum(scores) / len(scores)
            totalp += sum(pscores) / len(pscores)
        msg = 'Total = %.2f (%.2f + %.2f)' % (total + totalp, total, totalp)
        print(msg)
        log.write(msg + '\n')


def score_all_solutions(tag):
    def action(*args, **kargs):
        return None
    score_all_solutions_internal(tag, action)


def score_and_mark_all_solutions(tag):
    def action(f, scores, pscores):
        with io.open(f['fname'], 'r') as h:
            sol = json.loads(h.read())
        with io.open(f['fname'], 'w') as h:
            for i, v in enumerate(scores):
                sol[i]['score'] = scores[i]
                sol[i]['pscore'] = pscores[i]
            h.write(json.dumps(sol))
    score_all_solutions_internal(tag, action)


def compare_solutions(tag1, tag2):
    files = zip(filter_solutions(tag1), filter_solutions(tag2))
    total = 0
    with io.open('log_diff_%s-%s.txt' % (tag1, tag2), 'w') as log:
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


if __name__ == '__main__':
    send_all_solutions(sys.argv[1])
