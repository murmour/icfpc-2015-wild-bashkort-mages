'''
Created on Aug 8, 2015

@author: linesprower
'''

import io, json
import icfp_api

template = '''
    <html>
    <head>
        <style>
        td.max {
            background-color: lightgreen;
        }  
        td.min {
            background-color: #ffa0a0;
        }      
        </style>
    </head>
    <body>%s</body>
    </html>
    '''

def make_html(table):
    def f(x):
        if x.__class__.__name__ == 'int':
            return x
        return -1
    
    def make_row(data):
        mx = max([f(x) for x in data[1:]])
        mi = min([f(x) for x in data[1:]])
        def cl(x):
            if x == mx:
                return ' class="max"'
            if x == mi:
                return ' class="min"'
            return ''
        
        return '<tr>%s</tr>' % ''.join('<td%s>%s</td>' % (cl(x), x) for x in data)    
        
    res = '<table>%s</table>' % '\n'.join(make_row(row) for row in table)
    return template % res

def compare(tags):
    table = {} # id -> row
    n_seeds = [1,1,10,5,50,10,50,5,10,5,1,5,10,1,1,1,1,1,1,1,1,1,1,1,1]
    
    totals = [0] * len(tags)
    for i, tag in enumerate(tags):
        files = [x['fname'] for x in icfp_api.filter_solutions(tag)]        
        for fname in files:
            ident = None
            with io.open(fname, 'r') as f:
                sols = json.loads(f.read())
                score = 0
                fail = False
                for sol in sols:
                    if ident == None:
                        ident = sol['problemId']
                    else:
                        if ident != sol['problemId']:
                            print('different ids in file %s: %d and %d' % (fname, ident, sol['problemId']))
                            fail = True
                            break
                    if 'score' in sol and 'pscore' in sol:
                        score += sol['score'] + sol['pscore']
                    elif 'my_score' in sol:
                        score += sol['my_score']
                    else:
                        print('no score info in file %s' % fname)
                        fail = True
                        break
                if fail:
                    continue                
                if len(sols) != n_seeds[ident]:
                    print('unexpected number of games in file %s: %d instead of %d' % (fname, len(sols), n_seeds[ident]))
                    continue
                ident = int(ident)
                if ident not in table:
                    table[ident] = [ident] + ['?' for _ in range(len(tags))] 
                table[ident][i+1] = score // len(sols)
                totals[i] += score // len(sols)
    
    table = list(table.values())
    table.sort(key=lambda x: x[0])
    table = [['id'] + tags] + table + [['Total'] + totals]
    #print(table)
    with io.open('table.html', 'w') as res:
        res.write(make_html(table))
    print('Done!')        
    


def main():
    compare(['monday-morning-18_1', 'what-we-sent-18_1', 'fixed-potential_1', 'panopticum_666'])
    return

    fname = '../../data/solutions/solution_4_rdpacker_1.json'
    with io.open(fname) as f:
        data = json.loads(f.read())
        useds = [x['units_used'] for x in data]
        print(useds)
        print('sum = ', sum(useds))
        print('Min = ', min(useds))
        print('Idx = ', useds.index(min(useds)))
        
        

if __name__ == '__main__':
    main()
