
import sys
import icfp_api
import io
import json
import time
import rater
from runner import runProblem


def gen_discovery_solution(executable, problem, words):
    sol_js = runProblem(executable, problem, words)
    if sol_js == None:
        print('Solving failed')
        return None
    for p in sol_js:
        for w in words:
            if not (w in p['solution']):
                print('Solution does not contain word %s!' % w)
                return None
    return sol_js


def send_discovery_solution(sol_js, tag):
    sol_file = '../../discovery.json'
    for p in sol_js:
        p['tag'] = tag
    with io.open(sol_file, 'w') as h:
        h.write(json.dumps(sol_js))
    icfp_api.send_solution(sol_file)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: powerCheck.py executable problem_id words')
        sys.exit(1)

    executable = sys.argv[1]
    problem_id = int(sys.argv[2])
    problem = icfp_api.filter_problems(problem_id, problem_id)[0]
    words = sys.argv[3].replace('"', '\'').split(',')

    sol_js = gen_discovery_solution(executable, problem, words)
    if sol_js == None:
        sys.exit(1)

    tag = 'discovery_' + time.strftime("%H:%M:%S")
    send_discovery_solution(sol_js, tag)

    while True:
        print('waiting...')
        time.sleep(60)
        scores = rater.get_our_scores()
        if tag in scores[problem_id][3]:
            print('got score:')
            print(scores[problem_id])
            sys.exit(0)
