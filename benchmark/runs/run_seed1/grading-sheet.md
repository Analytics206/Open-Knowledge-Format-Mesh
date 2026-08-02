# Grading sheet

Arm labels are deliberately absent. Mark each claim hit or missed, then note any
statement that is false — an omission is a gap, a false statement is a defect and
should be traced to the concept that caused it.

## ca86a3ec7663

*Shape:* why

Claims:
- [ ] refreshing it automatically would erase the very signal drift exists to carry
- [ ] clearing drift is a human act — it asserts somebody reviewed the concept against its source
- [ ] `revalidate` rejects a `process:` actor and requires `human:`
- [ ] drift is observed at build time and cached; nothing resolves it at read time

False statements:

- 

## ebd0ecab2c5a

*Shape:* why

Claims:
- [ ] traversal, impact analysis and drift propagation all read an edge as fact
- [ ] a wrong typed edge is worse than a missing one
- [ ] relations require a human; a model-tier component may propose them but not write them
- [ ] an unknown predicate is rejected outright, unlike an unknown type which only warns

False statements:

- 

## a8df4ee284cf

*Shape:* why

Claims:
- [ ] `exclude` controls what the build READS; `bundles` controls what the mesh IS
- [ ] the build stops mirroring the folder, but a `bundles` entry still names it, so every reader still finds it by path
- [ ] the fix is to remove the `bundles.<id>` line, not to add another exclude
- [ ] keeping both is correct when the folder is an in-place bundle the build must not mirror

False statements:

- 

## 6a55f6c7fc7b

*Shape:* why

Claims:
- [ ] a later step would read what the failed step did not write
- [ ] that produces a second, misleading failure
- [ ] the misleading one is the failure people chase

False statements:

- 

## 4f6a5ff7439d

*Shape:* why

Claims:
- [ ] the level 2 / level 3 boundary is exactly the `model` line
- [ ] it is mechanically checked — `dev/check_levels.py` admits nothing beyond `human` at level 2
- [ ] it is named Level 2+ for what it costs an adopter, which is a name and not a relocation
- [ ] the component still declares `needs-model` and still sits in the level 3 bundle

False statements:

- 

## ce9491141ab5

*Shape:* why

Claims:
- [ ] neither — there is a third state, `unknown`
- [ ] the three states are match, drifted, and unknown
- [ ] defaulting an unobserved pointer to fresh would be a stored opinion wearing a computed one's clothes
- [ ] the cache stores observations, not verdicts, which is why caching it does not violate derive-don't-store

False statements:

- 

## 4897b1dfae21

*Shape:* why

Claims:
- [ ] refreshing it automatically would erase the very signal drift exists to carry
- [ ] clearing drift is a human act — it asserts somebody reviewed the concept against its source
- [ ] `revalidate` rejects a `process:` actor and requires `human:`
- [ ] drift is observed at build time and cached; nothing resolves it at read time

False statements:

- 

## 39553ae0f883

*Shape:* change-site

Claims:
- [ ] remove that bundle's entry from `bundles` in the config
- [ ] the build deletes member concepts it wrote itself, in the mesh's own `members/` folder
- [ ] a member concept the build did not write is reported and left alone rather than deleted
- [ ] the config check reports the bundle folder still sitting in the output directory

False statements:

- 

## 94c99148dabe

*Shape:* why

Claims:
- [ ] the level 2 / level 3 boundary is exactly the `model` line
- [ ] it is mechanically checked — `dev/check_levels.py` admits nothing beyond `human` at level 2
- [ ] it is named Level 2+ for what it costs an adopter, which is a name and not a relocation
- [ ] the component still declares `needs-model` and still sits in the level 3 bundle

False statements:

- 

## f3e80f90763a

*Shape:* why

Claims:
- [ ] traversal, impact analysis and drift propagation all read an edge as fact
- [ ] a wrong typed edge is worse than a missing one
- [ ] relations require a human; a model-tier component may propose them but not write them
- [ ] an unknown predicate is rejected outright, unlike an unknown type which only warns

False statements:

- 

## f31c0ace5e2d

*Shape:* why

Claims:
- [ ] a later step would read what the failed step did not write
- [ ] that produces a second, misleading failure
- [ ] the misleading one is the failure people chase

False statements:

- 

## 14a0a4f854fa

*Shape:* why

Claims:
- [ ] `exclude` controls what the build READS; `bundles` controls what the mesh IS
- [ ] the build stops mirroring the folder, but a `bundles` entry still names it, so every reader still finds it by path
- [ ] the fix is to remove the `bundles.<id>` line, not to add another exclude
- [ ] keeping both is correct when the folder is an in-place bundle the build must not mirror

False statements:

- 

## 9decc24965a9

*Shape:* lookup

Claims:
- [ ] Python 3.13
- [ ] standard library only — no third-party packages
- [ ] no install step; the folder is copied and run

False statements:

- 

## ff9b4c948cf8

*Shape:* lookup

Claims:
- [ ] Python 3.13
- [ ] standard library only — no third-party packages
- [ ] no install step; the folder is copied and run

False statements:

- 

## 44a65d8fca17

*Shape:* change-site

Claims:
- [ ] remove that bundle's entry from `bundles` in the config
- [ ] the build deletes member concepts it wrote itself, in the mesh's own `members/` folder
- [ ] a member concept the build did not write is reported and left alone rather than deleted
- [ ] the config check reports the bundle folder still sitting in the output directory

False statements:

- 

## 73158f2d04af

*Shape:* why

Claims:
- [ ] neither — there is a third state, `unknown`
- [ ] the three states are match, drifted, and unknown
- [ ] defaulting an unobserved pointer to fresh would be a stored opinion wearing a computed one's clothes
- [ ] the cache stores observations, not verdicts, which is why caching it does not violate derive-don't-store

False statements:

- 
