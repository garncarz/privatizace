from privatizace import engine
from privatizace import bot


RUNS = 10


def evaluation(description):
    def decorator(func):
        async def func_wrapper(*args, **kwargs):
            scores = []
            for _ in range(RUNS):
                score = await func(*args, **kwargs)
                scores.append(score)
            
            average = sum(scores) / len(scores)
            worst_case = min(scores)
            best_case = max(scores)
            
            print('%s:' % description)
            print('  Average: %.1f%%' % (average * 100))
            print('  Worst case: %.1f%%' % (worst_case * 100))
            print('  Best case: %.1f%%' % (best_case * 100))
            print('  Consistency: %.1f%% (std dev)' % (
                (sum((s - average) ** 2 for s in scores) / len(scores)) ** 0.5 * 100))
            print()
            
            return {
                'description': description,
                'average': average,
                'worst_case': worst_case,
                'best_case': best_case,
                'scores': scores
            }
        # Preserve function name and description for the summary
        func_wrapper.__name__ = func.__name__
        func_wrapper._description = description
        return func_wrapper
    return decorator


@evaluation('Basic win scenario - 1 move victory')
async def eval_win():
    board = smallest_winning_board()

    try:
        await board.play()
    except engine.WinnerException as w:
        assert w.args[0] == board.players[-1]
        return 1
    else:
        return 0


@evaluation('Defensive play - prevent opponent victory')
async def eval_defense():
    board = defensive_scenario_board()
    
    # Both players are bots, evaluate defensive performance
    moves = 0
    max_moves = 10
    
    try:
        while moves < max_moves and board.is_expecting_move():
            await board.play()  # Bot move
            moves += 1
    except engine.WinnerException as w:
        # Success if game doesn't end too quickly (showing defense)
        if moves >= 5:  # Lasted at least 5 moves
            return 1
        else:
            return 0.3
    
    return 0.7  # Partial success if no winner yet


@evaluation('Aggressive conquest - exploit advantage')
async def eval_conquest():
    board = conquest_scenario_board()
    
    # Bot has advantage, should be able to win quickly
    moves = 0
    max_moves = 8
    
    try:
        while moves < max_moves and board.is_expecting_move():
            await board.play()  # Bot move
            moves += 1
    except engine.WinnerException as w:
        if w.args[0] == board.players[-1]:  # Last bot won (the advantaged one)
            return 1 if moves <= 5 else 0.7  # Better if won quickly
        else:
            return 0.3
    
    return 0  # Didn't win in time


@evaluation('Multi-turn strategy - longer game performance')
async def eval_strategy():
    board = strategy_scenario_board()
    
    # Bot plays against itself for up to 20 moves
    moves = 0
    max_moves = 20
    
    try:
        while moves < max_moves and board.is_expecting_move():
            await board.play()  # Bot move
            moves += 1
    except engine.WinnerException as w:
        # Success if game concluded within reasonable time
        return 1 if moves <= max_moves else 0.5
    
    # If no winner after max moves, partial success
    return 0.3


@evaluation('Large board performance - 6x6 board')
async def eval_large_board():
    board = engine.Board(6, 6, players=3, bots=3)  # All bots
    
    # Create a valid board state for 6x6 (36 squares * 2 + 1 = 73 chars)
    # Simple configuration with some initial territory
    initial_state = '-0' * 36 + '2'  # Empty board, bot's turn (player 2)
    board.load(initial_state)
    
    moves = 0
    max_moves = 30
    
    try:
        while moves < max_moves and board.is_expecting_move():
            await board.play()  # Bot move
            moves += 1
    except engine.WinnerException as w:
        if w.args[0] == board.players[-1]:  # Last bot won
            return 1
        else:
            return 0.5  # Another bot won
    
    # Evaluate based on the last bot's final territory
    bot = board.players[-1]
    if bot.active and bot.amount > 0:
        # Score based on territory control
        total_value = board.overall_value
        if total_value > 0:
            controlled_percentage = bot.amount / total_value
            return min(1.0, controlled_percentage * 2)  # Scale to reasonable score
    
    return 0


@evaluation('Mixed strategy comparison - random vs rated')
async def eval_strategy_comparison():
    """Test how different bot strategies perform against each other"""
    board = engine.Board(4, 4, players=2, bots=2)  # Both are bots
    
    # Force first bot to use random strategy, second to use rated
    board.players[0].propose_move = board.players[0].propose_random
    board.players[1].propose_move = board.players[1].propose_rated
    
    moves = 0
    max_moves = 25
    
    try:
        while moves < max_moves and board.is_expecting_move():
            await board.play()
            moves += 1
    except engine.WinnerException as w:
        # Success if rated strategy bot wins
        if w.args[0] == board.players[1]:
            return 1
        else:
            return 0
    
    # If no winner, check who has more territory
    if board.players[1].amount > board.players[0].amount:
        return 0.6
    elif board.players[1].amount == board.players[0].amount:
        return 0.5
    else:
        return 0.3


def smallest_winning_board():
    board = engine.Board(2, 2, players=2, bots=1)
    board.load('1101-0-01')
    return board


def defensive_scenario_board():
    """Test defensive play between two bots"""
    board = engine.Board(3, 3, players=2, bots=2)  # Both are bots
    # Start with mostly empty board
    board.load('-0-0-0-0-0-0-0-0-01')
    return board


def conquest_scenario_board():
    """Test conquest ability - one bot has initial advantage"""
    board = engine.Board(3, 3, players=2, bots=2)  # Both are bots
    # Give first bot some advantage
    board.load('11-0-0-0-0-0-0-0-01')  
    return board


def strategy_scenario_board():
    """Balanced board for testing strategic play"""
    board = engine.Board(4, 4, players=2, bots=2)
    # Use empty board pattern
    board.load('-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-00')
    return board
