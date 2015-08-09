
from os import system
from icfp_api import team_id


def get_our_scores():
    system('rm rankings.js')
    system('wget https://davar.icfpcontest.org/rankings.js')
    s = open('rankings.js').readline()[len('var data = '):]
    d = eval(s)
    time = d['time']
    print(time)
    maps = d['data']['settings']
    scores = {}

    for m in maps:
        setting = m['setting']
        for scr in m['rankings']:
            if scr['teamId'] == team_id:
                scores[setting] = (scr['rank'], scr['score'],
                                   scr['power_score'], scr['tags'])
                break

    for s in scores:
        print(s, scores[s])


if __name__ == '__main__':
    get_our_scores()
