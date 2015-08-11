'''
Created on Aug 8, 2015

@author: linesprower
'''

import sys
import icfp_api


if __name__ == '__main__':
    if len(sys.argv) == 1:
        icfp_api.score_and_mark_all_solutions(None)
    elif len(sys.argv) == 2:
        icfp_api.score_and_mark_all_solutions(sys.argv[1])
    else:
        print('Usage: scorer.py tag')
        sys.exit(1)
