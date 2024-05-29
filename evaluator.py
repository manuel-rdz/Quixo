import copy
from tabulate import tabulate

from collections import defaultdict

class QuixoReferee:
    def __init__(self, player1, player2):
        self.board = [[0] * 5 for _ in range(5)]
        # 1
        self.player1 = player1
        # -1
        self.player2 = player2

    # it can happen that both players win at the same time.
    # if this happens, the player that is not his turn wins.
    def __is_winning_position(self, board, symbol):
        # check rows, cols and diagonals
        pos_symbol_wins = False
        neg_symbol_wins = False

        lr_diag_sum = 0
        rl_diag_sum = 0
        for i in range(5):
            col_sum = 0
            row_sum = 0
            for j in range(5):
                col_sum += board[j][i]
                row_sum += board[i][j]
            
            if col_sum == 5 or row_sum == 5:
                pos_symbol_wins = True
            
            if col_sum == -5 or row_sum == -5:
                neg_symbol_wins = True

            lr_diag_sum += board[i][i]
            rl_diag_sum += board[i][-(i+1)]

        if lr_diag_sum == 5 or rl_diag_sum == 5:
            pos_symbol_wins = True
        
        if lr_diag_sum == -5 or rl_diag_sum == -5:
            neg_symbol_wins = True
        
        if pos_symbol_wins and neg_symbol_wins:
            return True, (symbol * -1)
        elif pos_symbol_wins:
            return True, 1
        elif neg_symbol_wins:
            return True, -1

        return False, 0

    def __move_right(self, board, row, col, end_col=4):
        if col == 4:
            print("Referee::Invalid move. Called move_right with coordinates ", row, col)
            return board
        
        aux = board[row][col]
        for i in range(col + 1, end_col + 1):
            board[row][i-1] = board[row][i]

        board[row][end_col] = aux

        return board

    def __move_left(self, board, row, col, end_col=0):
        if col == 0:
            print("Referee::Invalid move. Called move_left with coordinates ", row, col)
            return board
        
        aux = board[row][col]
        for i in range(col - 1, end_col-1, -1):
            board[row][i+1] = board[row][i]
        
        board[row][end_col] = aux
        return board

    def __move_up(self, board, row, col, end_row = 0):
        if row == 0:
            print("Referee::Invalid move. Called move_up with coordinates ", row, col)
            return board
        
        aux = board[row][col]
        for i in range(row-1, end_row-1, -1):
            board[i+1][col] = board[i][col]
        
        board[end_row][col] = aux
        return board
    
    def __move_down(self, board, row, col, end_row=4):
        if row == 4:
            print("Referee::Invalid move. Called move_down with coordinates ", row, col)
            return board

        aux = board[row][col]
        for i in range(row + 1, end_row+1):
            board[i-1][col] = board[i][col]

        board[end_row][col] = aux

        return board

    def __compare_with_movements_top_row(self, new_board, symbol):
        for i in range(5):
            if self.board[0][i] == (symbol * -1):
                continue
            
            original_symbol = self.board[0][i]
            self.board[0][i] = symbol

            self.__move_down(self.board, 0, i)
            if self.board == new_board:
                return True
            
            self.__move_up(self.board, 4, i)

            if i != 0:
                self.__move_left(self.board, 0, i)
                if self.board == new_board:
                    return True
                
                self.__move_right(self.board, 0, 0, i)
            
            if i != 4:
                self.__move_right(self.board, 0, i)
                if self.board == new_board:
                    return True
                self.__move_left(self.board, 0, 4, i)

            self.board[0][i] = original_symbol

        return False
    
    def __compare_with_movements_bottom_row(self, new_board, symbol):
        for i in range(5):
            if self.board[4][i] == (symbol * -1):
                continue

            original_symbol = self.board[4][i]
            self.board[4][i] = symbol

            self.__move_up(self.board, 4, i)
            if self.board == new_board:
                return True
            self.__move_down(self.board, 0, i)

            if i != 0:
                self.__move_left(self.board, 4, i)
                if self.board == new_board:
                    return True
                self.__move_right(self.board, 4, 0, i)

            if i != 4:
                self.__move_right(self.board, 4, i)
                if self.board == new_board:
                    return True
                self.__move_left(self.board, 4, 4, i)

            self.board[4][i] = original_symbol

        return False

    def __compare_with_movements_right_col(self, new_board, symbol):
        for i in range(5):
            if self.board[i][4] == (symbol * -1):
                continue

            original_symbol = self.board[i][4]
            self.board[i][4] = symbol

            self.__move_left(self.board, i, 4)
            if self.board == new_board:
                return True
            self.__move_right(self.board, i, 0)

            if i != 0:
                self.__move_up(self.board, i, 4)
                if self.board == new_board:
                    return True
                self.__move_down(self.board, 0, 4, i)

            if i != 4:
                self.__move_down(self.board, i, 4)
                if self.board == new_board:
                    return True
                self.__move_up(self.board, 4, 4, i)

            self.board[i][4] = original_symbol

        return False

    def __compare_with_movements_left_col(self, new_board, symbol):
        for i in range(5):
            if self.board[i][0] == (symbol * -1):
                continue
            
            original_symbol = self.board[i][0]
            self.board[i][0] = symbol

            self.__move_right(self.board, i, 0)
            if self.board == new_board:
                return True
            self.__move_left(self.board, i, 4)

            if i != 0:
                self.__move_up(self.board, i, 0)
                if self.board == new_board:
                    return True
                self.__move_down(self.board, 0, 0, i)

            if i != 4:
                self.__move_down(self.board, i, 0)
                if self.board == new_board:
                    return True
                self.__move_up(self.board, 4, 0, i)

            self.board[i][0] = original_symbol

        return False
    
    # deepcopy is very slow, so for each movement we are going to mutate
    # the original board and compare with the new_board. If there's not a match
    # we return the board to the original state and continue with the new movement
    def __is_valid_move(self, new_board, symbol):
        return (self.__compare_with_movements_top_row(new_board, symbol) or 
            self.__compare_with_movements_bottom_row(new_board, symbol) or 
            self.__compare_with_movements_right_col(new_board, symbol) or 
            self.__compare_with_movements_left_col(new_board, symbol))

    def __play_turn(self, player):
        print("Player", player.name, "turn!")
        new_board = player.play_turn(copy.deepcopy(self.board))
        if self.__is_valid_move(new_board, player.symbol):
            winning_pos, winning_sym = self.__is_winning_position(new_board, player.symbol)
            if winning_pos:
                print("Symbol", 'O' if winning_sym == -1 else 'X', "wins!")
                self.__print_board(self.board)
                return True, winning_sym
        else:
            print("Player", player.name, "made an illegal move. Loses automatically!")
            self.__print_board(new_board)
            return True, (player.symbol * -1)

        return False, 0

    def play_game(self, limit_turns):
        self.board = [[0] * 5 for _ in range(5)]

        for i in range(2 * limit_turns):
            if i % 2 == 0:
                print('------------', (i + 2) // 2, ' TURN ------------')
                wins, sym = self.__play_turn(self.player1)
            else:
                wins, sym = self.__play_turn(self.player2)

            if wins:
                return sym
        
        print("Limit of turns reached. Game ends in a draw.")
        return 0
    
    # Receives the number of games to play per match and
    # the maximum number of turns per game.
    def play_match(self, limit_games, limit_turns):
        score = defaultdict(int)
        symbol_p1 = -1
        symbol_p2 = 1       
        for i in range(limit_games):
            print("----------- STARTING GAME ", i + 1, "-----------")
            symbol_p1, symbol_p2 = symbol_p2, symbol_p1

            self.player1.reset(symbol_p1)
            self.player2.reset(symbol_p2)

            print(self.player1.name, 'with symbol', 'O' if symbol_p1 == -1 else 'X')
            print(self.player2.name, 'with symbol', 'O' if symbol_p2 == -1 else 'X') 

            winner = self.play_game(limit_turns)

            if self.player1.symbol == winner:
                print(self.player1.name, "WINS!")
                score[self.player1.name] += 1
            elif self.player2.symbol == winner:
                print(self.player2.name, "WINS!")
                score[self.player2.name] += 1
            else:
                score[self.player1.name] += 0.5
                score[self.player2.name] += 0.5

        print("MATCH RESULTS!")
        print(limit_games, "GAMES PLAYED!")
        print(self.player1.name, " vs ", self.player2.name)
        print(self.player1.name, ":", score[self.player1.name])
        print(self.player2.name, ":", score[self.player2.name])
        if (score[self.player1.name] > score[self.player2.name]): print(self.player1.name, "WINS!")
        elif (score[self.player1.name] < score[self.player2.name]): print(self.player2.name, "WINS!")
        else: print("IT'S A DRAW!") 


    def __print_board(self, board=None):
        if board is None:
            board = self.board
        headers = [""] + [str(i) for i in range(1, 6)]
        rows = [[str(i + 1)] + ['O' if cell == -1 else 'X' if cell == 1 else ' ' for cell in row] for i, row in enumerate(board)]
        print(tabulate(rows, headers=headers, tablefmt="grid"))

"""
referee = QuixoReferee(bot1, bot2)
referee.play_match(50, 100)
"""
