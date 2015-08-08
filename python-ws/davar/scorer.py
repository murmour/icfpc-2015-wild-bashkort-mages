'''
Created on Aug 8, 2015

@author: linesprower
'''
import sys
import icfp_api

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: scorer.py solver version')
        sys.exit(1)
    icfp_api.send_all_solutions(sys.argv[1], int(sys.argv[2]))