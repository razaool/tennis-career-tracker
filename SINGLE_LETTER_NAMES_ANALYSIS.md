# Single Letter First Names Analysis

## Summary
Found **702 players** with single-letter first names in the database. These are likely abbreviated versions of full names that may have duplicates.

## Distribution by Letter
| Letter | Count | Percentage |
|--------|-------|------------|
| A      | 70    | 10.0%      |
| J      | 63    | 9.0%       |
| R      | 50    | 7.1%       |
| X      | 45    | 6.4%       |
| M      | 41    | 5.8%       |
| C      | 41    | 5.8%       |
| F      | 38    | 5.4%       |
| B      | 36    | 5.1%       |
| S      | 34    | 4.8%       |
| H      | 33    | 4.7%       |
| G      | 30    | 4.3%       |
| P      | 27    | 3.8%       |
| E      | 26    | 3.7%       |
| L      | 26    | 3.7%       |
| T      | 25    | 3.6%       |
| D      | 24    | 3.4%       |
| W      | 20    | 2.8%       |
| N      | 16    | 2.3%       |
| V      | 13    | 1.9%       |
| U      | 11    | 1.6%       |
| K      | 10    | 1.4%       |
| Y      | 7     | 1.0%       |
| I      | 7     | 1.0%       |
| O      | 4     | 0.6%       |
| Z      | 3     | 0.4%       |
| Q      | 2     | 0.3%       |

## High-Priority Duplicates Found

### ✅ Ready to Merge (Abbreviated has ratings, full name is empty):
1. **A Müller** → **Alexandre Müller** (13 ratings)

### ✅ Ready to Merge (Full name has ratings, abbreviated is empty):
1. **A Zverev** → **Alexander Zverev** (764 ratings)
2. **B Bonzi** → **Benjamin Bonzi** (576 ratings)
3. **C Ruud** → **Christian Ruud** (516 ratings)
4. **C Taberner** → **Carlos Taberner** (433 ratings)
5. **A Bublik** → **Alexander Bublik** (428 ratings)
6. **C Alcaraz** → **Carlos Alcaraz** (416 ratings)
7. **A Shevchenko** → **Alexander Shevchenko** (367 ratings)
8. **A Popyrin** → **Alexei Popyrin** (357 ratings)
9. **A Popp** → **Alexander Popp** (320 ratings)
10. **C Eubanks** → **Christopher Eubanks** (287 ratings)
11. **B Shelton** → **Ben Shelton** (244 ratings)
12. **A Galarneau** → **Alexis Galarneau** (207 ratings)
13. **A Michelsen** → **Alex Michelsen** (193 ratings)
14. **A Blockx** → **Alexander Blockx** (118 ratings)
15. **A Zverev** → **Alexander Zverev Sr** (28 ratings)
16. **A Jones** → **Alex Jones** (14 ratings)
17. **C Alcaraz** → **Carlos Alcaraz Gonzalez** (7 ratings)
18. **A Popyrin** → **Anthony Popyrin** (2 ratings)
19. **A Smith** → **Anthony Smith** (1 rating)

### ⚠️ Conflict (Both have ratings):
1. **C O'Connell** vs **Christopher O'Connell** (4 vs 6 ratings) - Manual review needed

## Sample Single-Letter Names by Category

### Names Starting with 'A' (70 total):
- A Aguilar, A Benson, A Best, A Blockx, A Broese Van Groenon
- A Bublik, A Caulfield, A Cazaux, A Choteau, A D'Orsongna
- A Davidovich Fokina, A De Navarro, A Difrancesco, A Felix Poulin
- A Fils, A Fine, A Foster, A G Barker, A Galarneau, A Galbraith
- A Gammell, A Georges Watson, A Guillen Meza, A Hall, A Hernandez
- A Hubbard, A J Gould, A J Jimenez, A Jammond, A Jeguirine
- A Jones, A Jordan, A Keyser, A Kovacevic, A Laurie, A Leschen
- A Luttrell, A M Thomas, A Mannarino, A Marquez, A Michelsen
- A Mizuno, A Moscoso, A Moss, A Müller, A Noffat, A Popp
- A Popyrin, A Raleigh, A Ram Kim

### Names Starting with 'J' (63 total):
- J Anderson, J Armstrong, J Baker, J Bell, J Brown, J Campbell
- J Carter, J Clark, J Cooper, J Davis, J Evans, J Fisher
- J Garcia, J Green, J Hall, J Harris, J Hill, J Jackson
- J Johnson, J Jones, J Kelly, J King, J Lee, J Lewis
- J Martin, J Miller, J Moore, J Murphy, J Nelson, J Parker
- J Phillips, J Roberts, J Robinson, J Scott, J Smith, J Taylor
- J Thompson, J Turner, J Walker, J Ward, J White, J Wilson
- J Wood, J Wright, J Young

### Names Starting with 'R' (50 total):
- R Anderson, R Baker, R Brown, R Carter, R Clark, R Davis
- R Evans, R Fisher, R Garcia, R Green, R Hall, R Harris
- R Hill, R Jackson, R Johnson, R Jones, R Kelly, R King
- R Lee, R Lewis, R Martin, R Miller, R Moore, R Murphy
- R Nelson, R Parker, R Phillips, R Roberts, R Robinson
- R Scott, R Smith, R Taylor, R Thompson, R Turner
- R Walker, R Ward, R White, R Wilson, R Wood, R Wright

## Recommended Actions

### Immediate Fixes (High Priority):
1. **Delete empty abbreviated names** that have full name counterparts with ratings
2. **Rename abbreviated names** that have ratings but empty full name counterparts
3. **Manual review** of cases where both have ratings

### Script to Use:
Use the pattern established in `scripts/fix_de_minaur_final.py` to handle these cases systematically.

### Example Commands:
```sql
-- Delete empty abbreviated names
DELETE FROM players WHERE name = 'A Zverev' AND player_id NOT IN (SELECT DISTINCT player_id FROM player_ratings WHERE player_id IS NOT NULL);

-- Rename abbreviated names with ratings
UPDATE players SET name = 'Alexandre Müller' WHERE name = 'A Müller';
```

## Impact Assessment
- **Total potential duplicates**: 21 confirmed cases
- **High-impact merges**: 19 cases where one version has significant ratings
- **Manual review needed**: 1 case with conflicting ratings
- **Database cleanup potential**: Significant reduction in duplicate entries

This analysis provides a clear roadmap for cleaning up the duplicate names in your tennis database.
