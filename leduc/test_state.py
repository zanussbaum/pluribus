import numpy as np
from leduc.state import State
from leduc.card import Card
from leduc.hand_eval import kuhn_eval


def test_turn():
    state = State([1, 2, 3], 2, 1, None)

    state.take('C')
    assert state.turn == 1

    state = State([1, 2, 3], 2, 1, None)

    state.take('F')
    state.take('C')
    state.take('C')

    assert state.turn == 1


def test_terminal():
    state = State([1, 2, 3], 2, 1, None)

    assert state.terminal is False, state

    state.take('F')

    assert state.terminal is True, state

    state = State([1, 2, 3], 3, 1, None)

    assert state.terminal is False, state

    state.take('F')

    assert state.terminal is False, state

    state.take('F')

    assert state.terminal is True, state


def test_terminal_multiround():
    state = State([1, 2, 3], 2, 1, None)

    assert state.terminal is False, state

    state.take('F')

    assert state.terminal is True, state

    state = State([1, 2, 3], 2, 2, None)

    state.take('C')
    assert state.terminal is False, state

    state.take('C')
    assert state.terminal is False, state

    state.take('C')
    assert state.terminal is False, state

    state.take('C')
    assert state.terminal is True, state

    state = State([1, 2, 3], 2, 2, None)

    state.take('C')
    assert state.terminal is False, state

    state.take('C')
    assert state.terminal is False, state

    state.take('C')
    assert state.terminal is False, state

    state.take('1R')
    assert state.terminal is False, state

    state = State([1, 2, 3], 2, 2, None)

    state.take('C')
    assert state.terminal is False, state

    state.take('C')
    assert state.terminal is False, state

    state.take('C')
    assert state.terminal is False, state

    state.take('1R')
    assert state.terminal is False, state

    state.take('1R')
    assert state.terminal is True, state


def test_terminal_after_raise():
    state = State([1, 2, 3], 2, 1, None)

    state = state.take('C', deep=True)
    state = state.take('1R', deep=True)

    assert state.terminal is False, state

    state = state.take('C', deep=True)

    assert state.terminal is True, state


def test_valid_actions():
    state = State([1, 2, 3], 2, 1, None)

    actions = state.valid_actions()
    assert actions == ['F', 'C', '1R'], actions

    state.take('C')
    actions = state.valid_actions()
    assert actions == ['F', 'C', '1R'], actions

    state = State([1, 2, 3], 2, 1, None)

    state.take('1R')
    actions = state.valid_actions()
    assert actions == ['F', 'C', '1R'], actions

    state.take('1R')
    actions = state.valid_actions()
    assert actions == ['F', 'C'], actions


def test_kuhn_utility():
    cards = [Card(14, 1), Card(13, 1), Card(12, 1)]
    state = State(cards, 2, 1, kuhn_eval)

    state.take('C')
    state.take('C')

    utility = state.utility()

    assert np.array_equal(utility, np.array([1, -1])), utility

    cards = [Card(14, 1), Card(13, 1), Card(12, 1)]
    state = State(cards, 2, 1, kuhn_eval)

    state.take('1R')
    state.take('C')

    utility = state.utility()

    assert np.array_equal(utility, np.array([2, -2])), utility
