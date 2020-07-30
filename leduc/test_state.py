from leduc.state import State


def test_turn():
    state = State(2, 1)

    state.take('C')
    assert state.turn == 1

    state = State(3, 2)

    state.take('F')
    state.take('C')
    state.take('C')

    assert state.turn == 1


def test_terminal():
    state = State(2, 1)

    assert state.terminal is False, state

    state.take('F')

    assert state.terminal is True, state

    state = State(3, 1)

    assert state.terminal is False, state

    state.take('F')

    assert state.terminal is False, state

    state.take('F')

    assert state.terminal is True, state


def test_terminal_multiround():
    state = State(2, 2)

    assert state.terminal is False, state

    state.take('F')

    assert state.terminal is True, state

    state = State(2, 2)

    state.take('C')
    assert state.terminal is False, state

    state.take('C')
    assert state.terminal is False, state

    state.take('C')
    assert state.terminal is False, state

    state.take('C')
    assert state.terminal is True, state

    state = State(2, 2)

    state.take('C')
    assert state.terminal is False, state

    state.take('C')
    assert state.terminal is False, state

    state.take('C')
    assert state.terminal is False, state

    state.take('1R')
    assert state.terminal is False, state

    state = State(2, 2)

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
