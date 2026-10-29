"""Official SNL regular-season ranking, independent of Excel formula caches.

Incomplete seasons or unresolved random draws do not produce official seeds.
"""
from collections import defaultdict
from itertools import combinations

TEAMS = ('Buffaloes','IHT','MORSL','Outcasts','Pacific Maul','Toronto Raccoons')


def _score(v):
    if v is None or str(v).strip() == '': return None
    s = str(v).strip()
    if not s.isdecimal(): raise ValueError(f'Invalid score {v!r}')
    return int(s)


def official_seeds(rows):
    stats = {t: dict(points=0, wins=0, rd=0, allowed=0, scored=0) for t in TEAMS}
    played = []
    for i in range(5, 66):
        row = rows.get(i,{})
        if not row.get('F') or not row.get('G'): continue
        a,h = row['F'],row['G']
        x,y = _score(row.get('H')), _score(row.get('I'))
        if x is None and y is None: return None
        if x is None or y is None: raise ValueError(f'Incomplete score row {i}')
        if a not in stats or h not in stats: raise ValueError(f'Unknown team row {i}')
        played.append((a,h,x,y))
        for t,for_,against in ((a,x,y),(h,y,x)):
            s=stats[t];s['scored']+=for_;s['allowed']+=against
            s['rd']+=max(-7,min(7,for_-against))
            s['points']+=2 if for_>against else 1 if for_==against else 0
            s['wins']+=int(for_>against)
    if len(played)!=60:return None

    def h2h(team, tied):
        pts=0
        for a,h,x,y in played:
            if a not in tied or h not in tied:continue
            if team==a:pts+=2 if x>y else 1 if x==y else 0
            if team==h:pts+=2 if y>x else 1 if x==y else 0
        return pts

    # Apply each criterion to the currently tied subgroup, recursively;
    # when one team separates, the remaining subgroup is evaluated anew.
    def rank(group, criterion=0):
        if len(group)<=1:return group
        if criterion>=6:
            return None  # Official random draw required, never guess.
        def value(t):
            s=stats[t]
            return (s['points'],s['wins'],h2h(t,set(group)),s['rd'],-s['allowed'],s['scored'])[criterion]
        buckets=defaultdict(list)
        for t in group:buckets[value(t)].append(t)
        if len(buckets)==1:return rank(group,criterion+1)
        out=[]
        for val in sorted(buckets,reverse=True):
            result=rank(buckets[val],criterion+1)
            if result is None:return None
            out.extend(result)
        return out
    return rank(list(TEAMS))
