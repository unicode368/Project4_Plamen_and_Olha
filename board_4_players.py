from player import Player
from graphics import Graphics
import random

board = []
player1 = Player()
player2 = Player()
player3 = Player()
player4 = Player()
turns_and_players = {1: player1, 2: player2, 3: player3, 4: player4}
safe_pos = [(2, 0), (4, 2), (2, 4), (0, 2)]
outer_boundaries = [0, 0, 4, 4]
inner_boundaries = [1, 1, 3, 3]
new_row_pos = 0
new_col_pos = 0
move_count = 0


def init_board():
    global board
    for i in range(5):
        row = []
        for j in range(5):
            row.append((i, j))
        board.append(row)


def init_players():
    global player1, player2, player3, player4
    # ( init_pos , symbol , color , stop_position)
    player1.set_player((4, 2), Graphics.SUITS[0], Graphics.COLORS[0], (4, 1))
    player2.set_player((2, 4), Graphics.SUITS[1], Graphics.COLORS[1], (3, 4))
    player3.set_player((0, 2), Graphics.SUITS[2], Graphics.COLORS[2], (0, 3))
    player4.set_player((2, 0), Graphics.SUITS[3], Graphics.COLORS[3], (1, 0))


def check_position(pos):  # returns a list of players at the input pos
    global player1, player2, player3, player4
    res = []
    if pos in player1.coins.values():
        res.append(("player1", player1.count_coins_in_pos(pos)))
    if pos in player2.coins.values():
        res.append(("player2", player2.count_coins_in_pos(pos)))
    if pos in player3.coins.values():
        res.append(("player3", player3.count_coins_in_pos(pos)))
    if pos in player4.coins.values():
        res.append(("player4", player4.count_coins_in_pos(pos)))
    return res


def print_board():
    for i in range(5):
        for j in range(5):
            curr_pos = check_position((i, j))  # curr_pos is a list of existing players at (i,j)
            one_pos_print = ""
            for k in curr_pos:
                if k[0] == "player1":
                    # one_pos_print += player1.color + player1.coin_avatar + str(k[1])
                    print(player1.color + player1.coin_avatar, str(k[1]), end="")
                elif k[0] == "player2":
                    # one_pos_print += player2.color + player2.coin_avatar + str(k[1])
                    print(player2.color + player2.coin_avatar, k[1], end="")
                elif k[0] == "player3":
                    # one_pos_print += player3.color + player3.coin_avatar + str(k[1])
                    print(player3.color + player3.coin_avatar, k[1], end="")
                elif k[0] == "player4":
                    # one_pos_print += player4.color + player4.coin_avatar + str(k[1])
                    print(player4.color + player4.coin_avatar, k[1], end="")
            if not curr_pos:
                print("\033[90m", "\033[1m", Graphics.EMPTY_POS, end="\t")
            else:
                print(one_pos_print, end="\t")
        print()


def check_game_end_condition():
    global player1, player2, player3, player4
    return player1.winning_order is not None and \
           player2.winning_order is not None and \
           player3.winning_order is not None and \
           player4.winning_order is not None


def is_safe_pos(pos):
    if pos in safe_pos:
        return True


def if_stuck_and_not_killed_then_move(player, dice_val):
    global move_count, new_row_pos, new_col_pos
    if (new_row_pos, new_col_pos) == player.stop_position:
        if move_count < dice_val and player.curr_coin != "c4":
            print("Player stuck...")
            player.set_curr_coin()
            print(player.curr_coin)
            curr_coin_pos = player.coins[player.curr_coin]
            new_row_pos = curr_coin_pos[0]
            new_col_pos = curr_coin_pos[1]
            move_count = 1
            return "continue"
        elif move_count == dice_val:
            print("Stop spot")
            return None
        elif (new_row_pos, new_col_pos) == player.stop_position and \
                move_count != dice_val and player.curr_coin == "c4":
            return "exit"
    else:
        return "go"


def make_move(player, dice_val):
    global move_count, new_row_pos, new_col_pos
    curr_coin_pos = player.coins[player.curr_coin]
    move_count = 1
    new_row_pos = curr_coin_pos[0]
    new_col_pos = curr_coin_pos[1]

    if player.check_boundaries() == "outer":
        boundaries = outer_boundaries
    else:
        boundaries = inner_boundaries

    while move_count <= dice_val:
        next_move = if_stuck_and_not_killed_then_move(player, dice_val)
        if next_move is None:
            break
        elif next_move == "exit":
            return
        elif next_move == "continue":
            continue
        elif next_move == "go":
            if new_col_pos == boundaries[0] \
                    and new_row_pos != boundaries[2]:
                new_row_pos += 1
            elif new_row_pos == boundaries[2] and \
                    new_col_pos != boundaries[3]:
                new_col_pos += 1
            elif new_col_pos == boundaries[3] and \
                    new_row_pos != boundaries[0]:
                new_row_pos -= 1
            elif new_row_pos == boundaries[0] and \
                    new_col_pos != boundaries[1]:
                new_col_pos -= 1
            move_count += 1
    if_kills_then_execute(player, new_row_pos, new_col_pos)


def if_kills_then_execute(player, new_row_pos, new_col_pos):
    new_pos_player = check_position((new_row_pos, new_col_pos))
    print("New position: ", new_row_pos, " ", new_col_pos)
    if is_safe_pos((new_row_pos, new_col_pos)):
        print("safe spot!")
        # if safe, set_coins updates curr_coin pos
        player.set_coins(player.curr_coin, (new_row_pos, new_col_pos))
    else:
        # if not the safe spot - refresh have_killed val and return killed coins to init_pos
        player.set_coins(player.curr_coin, (new_row_pos, new_col_pos))
        is_killed = False
        for player_in_the_spot in new_pos_player:
            print(player_in_the_spot)
            if int(player_in_the_spot[0][-1]) != turn:
                killed_player = turns_and_players[int(player_in_the_spot[0][-1])]
                for i in killed_player.coins.keys():
                    if killed_player.coins[i] == (new_row_pos, new_col_pos):
                        is_killed = True
                        killed_player.coins[i] = killed_player.init_pos
        if is_killed:
            player.set_have_killed()
            print("Someone gets killed!")


init_board()
init_players()
print("The game begins!")
turn = 1

while not check_game_end_condition():
    print()
    print_board()
    print()
    dice = random.randint(1, 4)
    if turn == 1:
        print(f"Player{turn} {player1.coin_avatar} will advance next by {dice} moves.")
        make_move(player1, dice)
    elif turn == 2:
        print(f"Player{turn} {player2.coin_avatar} will advance next by {dice} moves.")
        make_move(player2, dice)
    elif turn == 3:
        print(f"Player{turn} {player3.coin_avatar} will advance next by {dice} moves.")
        make_move(player3, dice)
    else:
        print(f"Player{turn} {player4.coin_avatar} will advance next by {dice} moves.")
        make_move(player4, dice)
    if turn == 4:
        turn = 1
    else:
        turn += 1
    cont = input("Continue...")
