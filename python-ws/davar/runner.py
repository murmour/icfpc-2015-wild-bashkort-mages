
import sys
import icfp_api
import json
import subprocess
import io


def runProblem(executable, p, words):
    print('running problem %s...' % p['id'])
    try:
        wordArgs = sum([ [ "-p", w ] for w in words ], [])
        solution = subprocess.check_output([executable, "-f", p['fname']]
                                           + wordArgs)
        print('ok')
        return json.loads(solution.decode('utf-8'))

    except subprocess.CalledProcessError as ex: # error code <> 0
        print("--------error--------")
        print(ex.cmd)
        print(ex.message)
        print(ex.returncode)
        return None


if __name__ == '__main__':
    if len(sys.argv) != 6:
        print('Usage: runner.py executable tag lowIndex highIndex words')
        sys.exit(1)

    executable = sys.argv[1]
    tag = sys.argv[2]
    words = sys.argv[5].replace('"', '\'').split(',')

    problems = icfp_api.filter_problems(int(sys.argv[3]), int(sys.argv[4]))
    for p in problems:
        sol_js = runProblem(executable, p, words)
        if sol_js != None:
            sol_file = '../../data/solutions/solution_%d_%s.json' % (p['id'], tag)
            with io.open(sol_file, 'w') as h:
                h.write(json.dumps(sol_js))
