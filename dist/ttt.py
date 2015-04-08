import random

from flask import Flask
from flask import json
from flask import jsonify
from flask import url_for
from flask import request
from flask import send_from_directory

app = Flask(__name__)


class Game(object):
  """Game object which holds all state information for game.

  Attributes:
    computer: String literal
    computer_board: List of ints representing computers moves
    computer_token: String representing token computer is using
    current_user: String representing current_user
    full_board: Dict of positions and players
    open_moves: list of ints representing unplayed moves
    player: String literal
    player_board: List of ints representing players moves
    player_token: String representing token player is using
    current_round: Int representing current round
    users: List of users
    winning_board_list: List of tuples indicating winning boards
  """

  def __init__(self):
    """Inits Game with initial playing state selecting a random first user."""
    x_token = 'X'
    o_token = 'O'
    self.computer = 'computer'
    self.player = 'player'
    self.users = [self.computer, self.player]
    self.current_round = 1
    self.winning_board_list = ((1, 2, 3),
                               (4, 5, 6),
                               (7, 8, 9),
                               (1, 4, 7),
                               (2, 5, 8),
                               (3, 6, 9),
                               (1, 5, 9),
                               (3, 5, 7))
    self.player_board = []
    self.computer_board = []
    self.full_board = []
    self.open_moves = range(1, 10)
    for square in self.open_moves:
      self.full_board.append({'square': square, 'user': '-'})
    self.current_user = random.choice(self.users)
    if self.current_user == self.computer:
      self.computer_token = x_token
      self.player_token = o_token
    else:
      self.computer_token = o_token
      self.player_token = x_token

  def is_over(self):
    """Indicates if game is over.

    Returns:
      True if game is over
    """
    if self.won_by():
      return True
    elif not self.open_moves:
      return True

  def get_current_user(self):
    """Indicates current user.

    Returns:
      String representing current_user
    """
    return self.current_user

  def won_by(self):
    """Indicates user who won the game.

    Returns:
      String representing user winning game
    """
    for board in self.winning_board_list:
      if len(set(board).intersection(set(self.player_board))) >= 3:
        return self.player
      elif len(set(board).intersection(set(self.computer_board))) >= 3:
        return self.computer

  def play(self, square):
    """Plays an open square.

    Args:
      square: Int representing square user is playing

    Raises:
      ValueError if square is already played or is invalid
    """
    if self.won_by():
      raise ValueError('Already won by {}'.format(self.won_by()))
    elif square in self.open_moves:
      active_user_board = getattr(self, self.current_user + '_board')
      active_user_board.append(square)
      del(self.open_moves[self.open_moves.index(square)])
      for position in self.full_board:
        if position['square'] == square:
          position['user'] = getattr(self, self.current_user + '_token')
      self.current_user = self.users[self.users.index(
            self.current_user)-1]
      self.current_round += 1
    else:
      raise ValueError('Invalid square or already taken: {}'.format(square))

  def copy(self):
    """Creates copy of game for trialing moves from current state.

    Returns:
      Game object
    """
    trial_game = Game()
    trial_game.player_board = self.player_board[:]
    trial_game.computer_board = self.computer_board[:]
    trial_game.current_user = self.current_user[:]
    trial_game.open_moves = self.open_moves[:]
    trial_game.current_round = self.current_round
    return trial_game


class GameCache(object):
  """Caches game objects in memory between sessions.

  Attributes:
    game_dict: Dict of games stored by ID
    counter: Int, next available ID
  """

  def __init__(self):
    """Inits GameCache with empty game_dict and counter."""
    self.game_dict = {}
    self.counter = 1

  def get(self, game_id):
    """Returns game from game_dict."""
    return self.game_dict[game_id]

  def put(self, game, game_id=None):
    """Stores a game.

    Args:
      game: Game object
      game_id: Int, existing ID (Optional)

    Returns:
      Int, ID of game
    """
    if game_id:
      self.game_dict[game_id] = game
    else:
      game_id = self.counter
      self.game_dict[game_id] = game
      self.counter +=1
    return game_id


def minimax(game):
  """Implementation of simplified minimax algorithm.

  For a given input game, trial possible game paths and provide optimal score
  for each user turn recursively until all paths are computed; return score.

  Args:
    game: Game object

  Returns:
    score: Score for game
  """
  score = None
  if game.is_over():
    if game.won_by() == game.player:
      return -1
    elif game.won_by() == game.computer:
      return 1
    else:
      return 0
  for move in game.open_moves:
    trial_game = game.copy()
    trial_user = trial_game.current_user
    trial_game.play(move)
    trial_score = minimax(game=trial_game)
    if trial_user == game.computer:
      if trial_score > score:
        score = trial_score
    elif trial_score < score or score is None:
      score = trial_score
  return score


def find_best_move(game, take_five=True):
  """Find the best open move.

  Args:
    game: Game object
    take_five: Bool, quick short circuit to always take 5 if open

  Returns:
    Int, best move (or random from set if multiple best moves found)
  """
  best_score = None
  choices = []
  if take_five and 5 in game.open_moves:
    return 5
  else:
    for move in game.open_moves:
      trial_game = game.copy()
      trial_game.play(move)
      score = minimax(trial_game)
      if score > best_score:
        best_score = score
        choices = [move]
      elif score == best_score:
        choices.append(move)
    if not choices:
      choices = game.open_moves
    return random.choice(choices)


def draw_board(game):
  """Returns a printable string formatting game board.

  Args:
    game: Game object

  Returns:
    String. Example:
      O O X
      4 X 6
      7 X 9
  """
  computer_board = game.computer_board
  player_board = game.player_board
  board_row_lists = []
  counter = 1
  for i in range(1, 4):
    board_row_list = []
    for n in range(3):
      if counter in computer_board:
        board_row_list.append('{} '.format(game.computer_token))
      elif counter in player_board:
        board_row_list.append('{} '.format(game.player_token))
      else:
        board_row_list.append('{} '.format(counter))
      counter += 1
    board_row_lists.append(''.join(board_row_list))
  return '\n'.join(board_row_lists)


def play():
  """Play tic tac toe.

  Prompts user for selection and plays game printing board on each user turn.
  """
  game = Game()
  print 'You are playing as {}'.format(game.player_token)
  print '{} goes first'.format(game.current_user)
  while not game.is_over():
    if game.current_user == game.player:
      print draw_board(game)
      print 'Your turn'
      move = int(input('Move: '))
      try:
        game.play(move)
      except ValueError as error:
        print error
    else:
      computer_move = find_best_move(game)
      print 'Computer move: {}'.format(computer_move)
      game.play(computer_move)
  print 'Game won by: {}'.format(game.won_by())
  print draw_board(game)


@app.route('/')
def ui():
  return app.send_static_file('index.html')
  #return url_for('/static/', filename='index.html')


@app.route('/api/', methods=['GET', 'POST'])
def api():
  """Play tic tac toe.

  Flask API which prompts user for selection and plays game on computers turn.

  Normal response example:
  {"computer_board": [5],
   "computer_token": "O",
   "current_user": "player",
   "error_list": [],
   "full_board": [
    {"square": 1, "user": "-"},
    {"square": 2, "user": "-"},
    {"square": 3, "user": "-"},
    {"square": 4, "user": "-"},
    {"square": 5, "user": "X"},
    {"square": 6, "user": "-"},
    {"square": 7, "user": "-"},
    {"square": 8, "user": "-"},
    {"square": 9, "user": "-"}],
   "game_id": 123,
   "is_over": null,
   "open_moves": [1, 3, 4, 6, 7, 8, 9],
   "player_board": [2],
   "player_token": "X",
   "won_by": null}

  Error response example:
    {"error_list": [
       "Game not found"]}

  Args:
    game: Game object
  """
  game = None
  error_list = []
  if request.method == 'GET':
    game_id = request.args.get('game_id')
    if game_id:
      try:
        game = game_cache.get(int(game_id))
      except KeyError as error:
        error_list.append('Game not found')
    else:
      error_list.append('Game not specified')
  if request.method == 'POST':
    request_obj = request.get_json(force=True)
    game_id = request_obj.get('game_id')
    move = request_obj.get('move')
    new = request_obj.get('new')
    if new:
      game_id = game_cache.put(Game())
    if game_id:
      game = game_cache.get(int(game_id))
      if game.current_user == game.computer:
          game.play(find_best_move(game))
      move = request.get_json(force=True).get('move')
      if move:
        try:
          move = int(move)
          game.play(move)
          if not game.is_over():
            game.play(find_best_move(game))
        except ValueError as error:
          error_list.append(str(error))
  if game:
    return jsonify(
        computer_board=game.computer_board,
        computer_token=game.computer_token,
        current_user=game.current_user,
        error_list=error_list,
        full_board=game.full_board,
        game_id=game_id,
        is_over=game.is_over(),
        open_moves=game.open_moves,
        player_board=game.player_board,
        player_token=game.player_token,
        won_by=game.won_by()
        )
  else:
    return jsonify(error_list=error_list)


if __name__ == '__main__':
  game_cache = GameCache()
  app.debug = True
  app.run(host='0.0.0.0', port=80)
