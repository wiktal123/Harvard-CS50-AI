"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    moves = 9 
    for row in board:
        moves -= row.count(EMPTY)
    if moves % 2 == 0:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    moves = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                moves.add((i, j))

    return moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    row = action[0]
    col = action[1]

    if board[row][col] != EMPTY:
        raise Exception("The move is invalid, please check your move")

    copiedBoard = copy.deepcopy(board)

    turn = player(copiedBoard)

    copiedBoard[row][col] = turn

    return copiedBoard


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for row in range(3):
        if board[row][0] == EMPTY:
            continue
        elif board[row][0] == board[row][1] and board[row][1] == board[row][2]:
            return board[row][0]

    for col in range(3):
        if board[0][col] == EMPTY:
            continue
        elif board[0][col] == board[1][col] and board[1][col] == board[2][col]:
            return board[0][col]

    if board[1][1] != EMPTY and (board[1][1] == board[0][2] and board[1][1] == board[2][0]) or \
            (board[1][1] == board[2][2] and board[1][1] == board[0][0]): return board[1][1]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) == None:
        for row in board:
            for tile in row:
                if tile == EMPTY:
                    return False
                
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    res = winner(board)

    if res == O:
        return -1
    elif res == X:
        return 1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    if terminal(board): return None

    if player(board) == X:
        currentRes = (None, -math.inf)
        for action in actions(board):
            score = algorythm_minimax(result(board,action), False)
            if score == 1: return action
            if score > currentRes[1]:
                currentRes=(action,score)
        return currentRes[0]

    else:
        currentRes = (None, math.inf)
        for action in actions(board):
            score = algorythm_minimax(result(board,action), True)
            if score == -1: return action
            if score < currentRes[1]:
                currentRes=(action,score)
        return currentRes[0]


def algorythm_minimax(board, maxMinTurn):
    if terminal(board): return utility(board)

    if maxMinTurn:
        currentScore = -math.inf

        for action in actions(board):
            newBoard = result(board, action)
            currentScore = max(algorythm_minimax(newBoard, False),currentScore)

        return currentScore

    else:
        currentScore = math.inf

        for action in actions(board):
            newBoard = result(board, action)
            currentScore = min(algorythm_minimax(newBoard, True),currentScore)

        return currentScore