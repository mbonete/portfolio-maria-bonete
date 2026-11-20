# Pacing the difficulty of 80 match-3 levels

Marine Wobbles, my match-3 for Android, has 80 levels in eight chapters, and each chapter adds a new mechanic. These are the rules that decide which levels are easy and which are hard, and the research each rule follows.

![Bar chart of the tier of each of Marine Wobbles' 80 levels, from tutorial to peak. The bars rise and fall in a sawtooth that climbs across the eight chapters, and the levels that teach a new mechanic sit low.](figure:level-tiers "The tier of each of the 80 levels, in eight chapters of ten. A dot marks a level that teaches a new mechanic.")

## 1. Let the average climb, with dips

The levels follow a rising sawtooth: the average difficulty climbs slowly, single levels go up and down, and every hard peak is followed by an easy level. Difficulty that rises as the player gets better is the core of flow theory ([Csikszentmihalyi](https://doi.org/10.1007/978-94-017-9088-8_16)).

## 2. Teach a new rule on a plain board

A player meeting a new rule has enough to take in. So the level that introduces a mechanic uses the plain default board: pieces fall straight down and nothing else unusual is on it. I check everything on the board, rather than only what changed since the last level, because a board can change one thing and still show the new rule beside two others the player hasn't met.

This follows cognitive load research. In [Pollock, Chandler and Sweller's experiments (2002)](https://doi.org/10.1016/S0959-4752(01)00016-0), novices learned complex material better when its elements came one at a time.

## 3. Teach, practise, then test

A mechanic is never introduced and tested in the same level. Levels come in short runs about one mechanic: the first teaches it, the next ones practise it and add a twist, and the last one tests it. Each run starts easy and ends hard, which is where the sawtooth comes from.

[Linehan and colleagues (CHI PLAY 2014)](https://hdl.handle.net/10468/3461) found the same structure in Portal, Portal 2 and Braid: each skill arrives alone in a simple puzzle, then gets practised and combined with earlier ones, and complexity climbs until the next skill arrives.

## 4. Climb one step at a time

Every level has a tier: tutorial, easy, medium, hard or peak. From one level to the next, difficulty climbs at most one tier, so an easy level is never followed by a hard one. Drops have no limit. There are never more than two hard levels in a row, and a peak is always followed by an easy level.

In player data from match-3 games at [EA (Xue et al. 2017)](https://archives.iw3c2.org/www2017/proceedings/companion/p465.pdf) and [Rovio (Roohi et al. 2020)](https://arxiv.org/abs/2008.12937), players left where difficulty spiked. Climbing one tier at a time keeps spikes out of the list.

The easy level after a peak is common design practice. The closest study, by [Gutwin and colleagues (CHI 2016)](https://doi.org/10.1145/2858036.2858419), found that 12 players rated match-3 sequences with easier boards in the middle and at the end as more fun.

## 5. Get new players to competence first

A first-time player doesn't know how to play yet, so the first chapter is about getting them there. The first open shows a short film of groups being tapped and one sentence with the rule, and level 1 points at a real group on the board. Every level opens on its goal in one line, each lesson teaches one mechanic in one short line, and the early boards are dealt in clumps so the groups are big. That help fades out over the first two chapters. Levels 1 to 10 hold nothing hard, and levels 11 to 30 no peak.

![Level 2: a group of purple octopuses popping for 1,500 points.](/marine-wobbles/board.webp "Level 2: a big group of octopuses pops for 1,500 points.")

[Self-determination theory](https://doi.org/10.1007/s11031-006-9051-8) links a player's sense of competence to how much they enjoy a game.

The game never changes a level based on how someone is playing, so every player gets the same levels. The move hint can be turned off, and no level is sized to need a rescue item.

## 6. Measure every level with bots

Each tier has a win-rate band. Seven strategy bots play every level 2,000 to 5,000 times each from fixed seeds, and tests hold every level to its tier's band and every tier to being harder than the one before.

## What the research doesn't cover

No study has compared a sawtooth with a steady climb, so the shape as a whole is untested. The win-rate bands are design defaults measured on bots, and the game collects no player data to check them against. Some studies point the other way: two found that matching difficulty to skill changed neither enjoyment nor play ([Cutting et al. 2023](https://doi.org/10.1098/rsos.220274); [Deterding and Cutting 2023](https://doi.org/10.1145/3611065)), and in a large educational game, players played longer when the game was easier ([Lomas et al. 2013](https://doi.org/10.1145/2470654.2470668)).
