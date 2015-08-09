
import sys
import icfp_api
import io
import json
from runner import runProblem


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('Usage: powerCheck.py executable tag problem_id words')
        sys.exit(1)

    executable = sys.argv[1]
    tag = sys.argv[2]
    problem_id = int(sys.argv[3])
    words = sys.argv[4].replace('"', '\'').split(',')
    problem = icfp_api.filter_problems(problem_id, problem_id)[0]

    sol_js = runProblem(executable, problem, words)
    if sol_js == None:
        print('solving failed')
        sys.exit(1)

    for p in sol_js:
        for w in words:
            if not (w in p['solution']):
                print('Solution does not contain word %s!' % w)
                sys.exit(1)

    sol_file = '../../data/solutions/solution_%d_%s.json' % (problem_id, tag)
    for p in sol_js:
        p['tag'] = tag
    with io.open(sol_file, 'w') as h:
        h.write(json.dumps(sol_js))

    icfp_api.send_solution(sol_file)
