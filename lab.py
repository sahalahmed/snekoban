"""
6.1010 Spring '23 Lab 4: Snekoban Game
"""

import json
import typing

# NO ADDITIONAL IMPORTS!


direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    game = {
        "wall": set(),
        "computer": set(),
        "target": set(),
        "dimensions": (len(level_description), len(level_description[0])),
    }

    for row_index, row_content in enumerate(level_description):
        for col_index, col_content in enumerate(row_content):
            if "player" in col_content:
                game["player"] = (row_index, col_index)
            if "wall" in col_content:
                game["wall"].add((row_index, col_index))
            if "computer" in col_content:
                game["computer"].add((row_index, col_index))
            if "target" in col_content:
                game["target"].add((row_index, col_index))
    return game


def victory_check(game):
    """
    Given a game representation (of the form returned from new_game), return
    a Boolean: True if the given game satisfies the victory condition, and
    False otherwise.
    """
    if len(game["computer"]) == 0:
        return False
    if len(game["computer"]) != len(game["target"]):
        return False
    for target in game["target"]:
        if target not in game["computer"]:
            return False
    return True


def step_game(game, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of the following: {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    result_game = {
        "player": game["player"],
        "wall": game["wall"].copy(),
        "computer": game["computer"].copy(),
        "target": game["target"].copy(),
        "dimensions": game["dimensions"],
    }

    def direction_offset(direction, location):
        """
        Given a tuple representing an object's location, return an updated
        location tuple advanced one step in the specified direction.
        """
        if direction == "up":
            return (location[0] - 1, location[1])
        if direction == "down":
            return (location[0] + 1, location[1])
        if direction == "left":
            return (location[0], location[1] - 1)
        if direction == "right":
            return (location[0], location[1] + 1)

    one_step = direction_offset(direction, game["player"])
    two_step = direction_offset(direction, direction_offset(direction, game["player"]))

    if one_step in game["wall"]:
        return game
    if one_step in game["computer"]:
        if two_step in game["wall"]:
            return game
        if two_step in game["computer"]:
            return game
        result_game["computer"].remove(one_step)
        result_game["computer"].add(two_step)
    result_game["player"] = one_step

    return result_game


def dump_game(game):
    """
    Given a game representation (of the form returned from new_game), convert
    it back into a level description that would be a suitable input to new_game
    (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    level_description = [[] for _ in range(game["dimensions"][0])]
    for row in level_description:
        for _ in range(game["dimensions"][1]):
            row.append([])

    for location in game["wall"]:
        level_description[location[0]][location[1]].append("wall")
    for location in game["computer"]:
        level_description[location[0]][location[1]].append("computer")
    for location in game["target"]:
        level_description[location[0]][location[1]].append("target")
    level_description[game["player"][0]][game["player"][1]].append("player")

    return level_description


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from new game), find a
    solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    if victory_check(game):
        return []

    def get_neighbors(game, raw_state):
        """
        Given the starting game and the current state, returns neighbor states that
        have resulted in a succesful move, in the same form as the current state.
        """
        game_state = (raw_state[0], set(raw_state[1]))
        directions = ["up", "down", "left", "right"]
        neighbors = set()
        for direction in directions:
            temp_game = game.copy()
            temp_game["player"] = game_state[0]
            temp_game["computer"] = game_state[1]
            if step_game(temp_game, direction) != temp_game:
                computer_list = set()
                for computer in step_game(temp_game, direction)["computer"]:
                    computer_list.add(computer)
                neighbors.add(
                    (
                        step_game(temp_game, direction)["player"],
                        tuple(computer_list),
                        direction,
                    )
                )
        return neighbors

    def solved_check(game, game_state):
        """
        Given a game state representation, return a Boolean: True if the given game
        satisfies the victory condition, and False otherwise.
        """
        for computer in game_state[1]:
            if computer not in game["target"]:
                return False
        return True

    initial_computer = set()
    for location in game["computer"]:
        initial_computer.add(location)

    paths = [
        [
            [game["player"], tuple(initial_computer)],
        ]
    ]
    visited = {(game["player"], tuple(initial_computer))}

    while paths:
        path = paths.pop(0)
        game_state = path[-1]
        for neighboring_state in get_neighbors(game, game_state):
            if (neighboring_state[0], neighboring_state[1]) not in visited:
                temp_path = path[:]
                temp_path.append(neighboring_state)
                if solved_check(game, neighboring_state):
                    result = [result_state[2] for result_state in temp_path[1:]]
                    return result
                else:
                    paths.append(temp_path)
                    visited.add((neighboring_state[0], neighboring_state[1]))
    return None


if __name__ == "__main__":
    pass
