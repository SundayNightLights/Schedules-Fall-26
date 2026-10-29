from playoff_engine import bracket, series_result

seeds = ['Buffaloes', 'IHT', 'MORSL', 'Outcasts', 'Pacific Maul', 'Toronto Raccoons']
assert bracket(None, {}) == {}
start = bracket(seeds, {})
assert len(start) == 2 and all(x.game3 == 'potential' for x in start.values())
# Higher seed wins both: game 1 home, game 2 away.
sweep = bracket(seeds, {70:(1,2), 72:(2,1)})
assert sweep['QF_3v6'].winner == 'MORSL'
assert sweep['QF_3v6'].game3 == 'not_needed'
# Split series: game 3 required.
split = bracket(seeds, {70:(1,2), 72:(1,2)})
assert split['QF_3v6'].winner is None and split['QF_3v6'].game3 == 'required'
# Full bracket: QF high seeds advance, SF top seeds advance, final top seed wins.
scores = {70:(1,2),72:(2,1),71:(1,2),73:(2,1),
          77:(1,2),79:(2,1),78:(1,2),80:(2,1),
          84:(1,2),85:(2,1)}
full = bracket(seeds, scores)
assert full['SF_1'].higher == 'Buffaloes' and full['SF_1'].lower == 'Outcasts'
assert full['SF_2'].higher == 'IHT' and full['SF_2'].lower == 'MORSL'
assert full['FINAL'].higher == 'Buffaloes' and full['FINAL'].lower == 'IHT'
assert full['FINAL'].winner == 'Buffaloes'
assert full['FINAL'].game3 == 'not_needed'
# Third game resolves split.
third = series_result('MORSL','Toronto Raccoons',(70,72,74),{70:(1,2),72:(1,2),74:(0,3)})
assert third.winner == 'MORSL' and third.game3 == 'completed'
print('PASS: unseeded, placeholders, sweep, split, Game 3, reseeding, semifinal and final advancement')
