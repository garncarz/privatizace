import pytest
import asyncio
from evaluation import bots


class TestBotEvaluation:
    """Tests for the bot evaluation system"""
    
    def test_evaluation_functions_exist(self):
        """Test that evaluation functions are properly defined"""
        eval_functions = [f for f in dir(bots) if f.startswith('eval_')]
        
        # Should have at least 6 evaluation scenarios
        assert len(eval_functions) >= 6
        
        expected_functions = [
            'eval_win', 'eval_defense', 'eval_conquest', 
            'eval_strategy', 'eval_large_board', 'eval_strategy_comparison'
        ]
        
        for func_name in expected_functions:
            assert func_name in eval_functions, f"Missing evaluation function: {func_name}"
    
    @pytest.mark.asyncio
    async def test_basic_evaluation_runs(self):
        """Test that basic evaluation can run without errors"""
        result = await bots.eval_win()
        
        # Check result structure
        assert isinstance(result, dict)
        assert 'average' in result
        assert 'worst_case' in result
        assert 'best_case' in result
        assert 'scores' in result
        
        # Check value ranges
        assert 0 <= result['average'] <= 1
        assert 0 <= result['worst_case'] <= 1
        assert 0 <= result['best_case'] <= 1
        assert len(result['scores']) == bots.RUNS
    
    @pytest.mark.asyncio
    async def test_conquest_evaluation_runs(self):
        """Test that conquest evaluation can run without errors"""
        result = await bots.eval_conquest()
        
        # Should return valid result structure
        assert isinstance(result, dict)
        assert 'average' in result
        assert 0 <= result['average'] <= 1
    
    @pytest.mark.asyncio
    async def test_defense_evaluation_runs(self):
        """Test that defense evaluation can run without errors"""
        result = await bots.eval_defense()
        
        # Should return valid result structure
        assert isinstance(result, dict)
        assert 'average' in result
        assert 0 <= result['average'] <= 1
    
    def test_board_scenarios_load_correctly(self):
        """Test that predefined board scenarios load without errors"""
        # Test board creation functions don't crash
        defensive_board = bots.defensive_scenario_board()
        conquest_board = bots.conquest_scenario_board()
        strategy_board = bots.strategy_scenario_board()
        
        # Basic validation
        assert defensive_board.width == 3
        assert defensive_board.height == 3
        assert conquest_board.width == 3
        assert conquest_board.height == 3
        assert strategy_board.width == 4
        assert strategy_board.height == 4
        
        # Check that all players are bots
        for board in [defensive_board, conquest_board, strategy_board]:
            for player in board.players:
                assert player.is_bot, "All players should be bots in evaluation scenarios"
    
    def test_runs_configuration(self):
        """Test that RUNS configuration is reasonable"""
        assert bots.RUNS >= 5, "Should run at least 5 iterations for statistical validity"
        assert bots.RUNS <= 50, "Should not run too many iterations for performance"