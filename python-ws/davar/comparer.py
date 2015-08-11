'''
Created on Aug 8, 2015

@author: linesprower
'''
import sys
import icfp_api


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: scorer.py tag1 tag2')
        sys.exit(1)
    icfp_api.compare_solutions(sys.argv[1], sys.argv[2])
