# Gen4 Battle Factory Team Builder

A PyQt5-based analysis tool for evaluating Pokémon matchups using deterministic damage-based heuristics.

The system evaluates potential team members using a damage model (hits dealt vs hits taken) and reports matchup performance as percentages over filtered opponent pools.

## Core Idea

Users can input:
- battle hints (context constraints)
- round number / progression stage

The system evaluates how each candidate Pokémon performs under those conditions and computes:

- percentage of Pokémon in the filtered pool that each candidate can defeat
- comparative strength of potential trades and team members
-  strict and relaxed accuracy models

## Features

- PyQt5 GUI for interactive evaluation
- Input-based filtering (hints, round state, constraints)
- Damage-potential heuristic model
- Win-rate percentage computation against filtered opponent pools
- Dual evaluation modes:
  - guaranteed-hit model (only 100% accuracy moves are considered for damage evaluation)
  - full-move model (all moves assumed to always hit, regardless of accuracy)

- Side-by-side comparison for trade decision support
- Interactive matchup testing against new Pokémon

## Key Insight

A simple damage-based heuristic, combined with filtered opponent evaluation, was effective at guiding in-run decision-making for team selection and trades.

Running both strict and relaxed models in parallel allowed informed risk decisions rather than purely deterministic selection.

## Tech Stack

- Python
- PyQt5
