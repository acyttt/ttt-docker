import unittest
import ttt


class TestTttPy(unittest.TestCase):

  def setup(self):
    pass

  def test_draw_board(self):
    """Printable board should be returned"""
    game = ttt.Game()
    test_board = '1 2 3 \n4 5 6 \n7 8 9 '
    self.assertEqual(ttt.draw_board(game), test_board)

  def test_find_best_move(self):
    """Should return best move"""
    game = ttt.Game()
    game.current_user = 'computer'
    game.player_board = [1]
    game.computer_board = []
    game.computer_token = 'O'
    game.player_token = 'X'
    game.open_moves = range(2, 10)
    self.assertEqual(ttt.find_best_move(game, take_five=False), 5)

  def test_minimax(self):
    """Test a bad move"""
    game = ttt.Game()
    game.current_user = 'computer'
    game.player_board = [1, 2]
    game.player_board = [5, 9, 4]
    game.computer_token = 'O'
    game.player_token = 'X'
    game.open_moves = range(2, 10)
    self.assertEqual(ttt.minimax(game), -1)


if __name__ == '__main__':
  unittest.main()
