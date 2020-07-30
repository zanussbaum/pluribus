from leduc.state import State


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


def test_valid_actions():
    state = State([1, 2, 3], 2, 1, None)

    actions = state.valid_actions()
    assert actions == ['F', 'C', 'R'], actions

    state.take('C')
    actions = state.valid_actions()
    assert actions == ['F', 'C', 'R'], actions

    state = State([1, 2, 3], 2, 1, None)

    state.take('1R')
    actions = state.valid_actions()
    assert actions == ['F', 'C', 'R'], actions

    state.take('1R')
    actions = state.valid_actions()
    assert actions == ['F', 'C'], actions
