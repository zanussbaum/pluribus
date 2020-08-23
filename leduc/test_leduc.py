import pytest

from leduc.state import Leduc as State


def test_valid_actions():
    state = State([i for i in range(6)], 2, None)

    state.take('C')
    new_state = state.take('C', deep=True)

    assert (state.valid_actions() == ['F', 'C', '2R'] and
           new_state.valid_actions() == ['F', 'C', '4R']), f'Actions {state.valid_actions()}'


    state = State([i for i in range(6)], 2, None)

    state = state.take('2R', deep=True)

    assert state.players[0].bets == 3, f'Bet {state.players[0].bets}'
    assert state.valid_actions() == ['F', 'C', '2R'], f'Actions {state.valid_actions()}'

    state = state.take('2R', deep=True)

    assert state.players[1].bets == 5, f'Bet {state.players[0].bets}'
    assert state.round == 0 and state.valid_actions() == ['F', 'C'], f'Actions {state.valid_actions()}'

    state = state.take('C', deep=True)

    assert all([p.bets == 5 for p in state.players]), f'Bet {state.players}'
    assert state.round == 1, f'Round {state.round}'


def test_terminal():
    state = State([i for i in range(6)], 2, None)

    state = state.take('F', deep=True)

    assert state.terminal == True, f'State {state}'

    state = State([i for i in range(6)], 2, None)
    state = state.take('C', deep=True)
    state = state.take('C', deep=True)
    state = state.take('C', deep=True)
    state = state.take('C', deep=True)

    assert state.terminal == True, f'State {state}'

    with pytest.raises(ValueError):
        state.take('1000R', deep=True)


def test_turn():
    state = State([i for i in range(6)], 2, None)

    assert state.turn == 0, f'State {state}'

    state = state.take('C', deep=True)
    assert state.turn == 1, f'State {state}'

    state = state.take('C', deep=True)
    assert state.turn == 0, f'State {state}'

    state = State([i for i in range(6)], 2, None)

    state = state.take('2R', deep=True)
    assert state.turn == 1, f'State {state}'

    state = state.take('2R', deep=True)
    assert state.turn == 0, f'State {state}'

    state = State([i for i in range(6)], 2, None)

    state = state.take('C', deep=True)
    assert state.turn == 1, f'State {state}'

    state = state.take('2R', deep=True)
    assert state.turn == 0, f'State {state}'

    state = state.take('2R', deep=True)
    assert state.turn == 1, f'State {state}'
