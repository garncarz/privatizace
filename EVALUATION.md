# Bot Effectiveness Evaluation System

This document describes the comprehensive bot effectiveness evaluation system that automatically tests bot reactions to predefined boards and measures their ability to conquer and defend territory.

## Overview

The evaluation system runs multiple scenarios to assess different aspects of bot performance:

- **Conquest abilities** - Can the bot capitalize on advantages and win games?
- **Defensive capabilities** - Can the bot prevent opponents from winning?
- **Strategic thinking** - How well does the bot perform in longer, complex games?
- **Scalability** - How does performance change on larger boards?
- **Strategy comparison** - How do different bot strategies compare?

## Running Evaluations

```bash
# Run the complete evaluation suite
python evaluate.py

# Run tests for the evaluation system
python -m pytest tests/test_evaluation.py
```

## Evaluation Scenarios

### 1. Basic Win Scenario
Tests the bot's ability to recognize and execute winning moves in simple 1-move victory situations.

### 2. Defensive Play
Evaluates how well bots can defend against aggressive opponents and prevent quick losses.

### 3. Aggressive Conquest  
Tests the bot's ability to exploit territorial advantages and convert them into victories.

### 4. Multi-turn Strategy
Assesses strategic thinking over longer games (up to 20 moves) with more complex decision-making.

### 5. Large Board Performance
Tests scalability on 6x6 boards with multiple opponents to evaluate performance in complex scenarios.

### 6. Strategy Comparison
Compares the effectiveness of different bot strategies (random vs. rated move selection).

## Metrics Reported

For each scenario, the system reports:

- **Average Performance**: Mean success rate across all runs
- **Worst Case**: Lowest performance observed  
- **Best Case**: Highest performance observed
- **Consistency**: Standard deviation showing performance variability

## Overall Results

The system provides:
- Overall average performance across all scenarios
- Performance ranking of scenarios (easiest to hardest)
- Statistical analysis for identifying strengths and weaknesses

## Configuration

### Adjusting Test Runs
Modify `RUNS` in `evaluation/bots.py` to change the number of iterations per scenario:

```python
RUNS = 10  # Number of times each scenario is tested
```

### Adding New Scenarios
Create new evaluation functions using the `@evaluation()` decorator:

```python
@evaluation('Your scenario description')
async def eval_your_scenario():
    # Your test logic here
    return 1.0  # Return score between 0.0 and 1.0
```

## Interpreting Results

- **70%+ performance**: Excellent - bot handles the scenario very well
- **50-70% performance**: Good - bot shows competent play with room for improvement  
- **30-50% performance**: Fair - bot struggles but shows some capability
- **<30% performance**: Poor - scenario reveals significant bot weaknesses

## Example Output

```
Defensive play - prevent opponent victory     70.0%
Large board performance - 6x6 board          61.3%
Mixed strategy comparison - random vs rated  50.0%
Basic win scenario - 1 move victory          50.0%
Aggressive conquest - exploit advantage      37.0%
Multi-turn strategy - longer game performance 30.0%
```

This shows the bot is strongest at defensive play but struggles with long-term strategic thinking.