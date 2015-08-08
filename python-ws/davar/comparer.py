'''
Created on Aug 8, 2015

@author: linesprower
'''
import sys
import icfp_api

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: scorer.py solver version1 version2')
        sys.exit(1)
    icfp_api.compare_solutions(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))