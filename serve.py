from flask import Flask, render_template, request, session, flash, redirect
from flask_socketio import SocketIO, join_room, leave_room, emit
from leduc.play.play import Game

app = Flask(__name__)
app.config['SECRET_KEY'] = 'poker'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
socketio = SocketIO(app)

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        if len(request.form['name']) < 1:
            flash('Pick a name')
        else:
            session['room'] = 'room'
            session['name'] = request.form['name']
            return redirect('/play')

    return render_template('home.html')
    
@app.route('/play', methods=['GET', 'POST'])
def start_game():
    if request.method == 'GET':
        return render_template('game.html') 

@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    join_room(room)
    emit('status', {'msg': session.get('name') + ' has entered the room.'}, room=room)

@socketio.on('text', namespace='/chat')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    emit('message', {'msg': session.get('name') + ': ' + message['msg']}, room=room)

@socketio.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)

@socketio.on('start', namespace='/chat')
def start(message):
    room = session.get('room')
    game = Game()
    game.start_game()
    emit('status', {'msg': "Starting the game. You are player 1"}, room=room)
    emit('status', {'msg': 'Your private card is {}'.format(game.cards[0])})
    session['game'] = game

    if game.state() == 0:
        emit('status', {'msg': "It's your turn. Choose an action"})
        emit('turn', {})

    else:
        action = game.pluribus_action()
        emit('status', {'msg': "Pluribus played {}".format(action)})

@socketio.on('turn', namespace='/chat')
def turn(message):
    game = session.get('game')
    if game.state() == 0:
        action = message['action']
        if message['action'] == 'Fold':
            game.user_action('F')
            emit('status', {'msg': "You played {}".format(action)})
        elif message['action'] == 'Call':
            game.user_action('C')
            emit('status', {'msg': "You played {}".format(action)})
        elif message['action'] == 'Raise':
            amount = message['amount']
            game.user_action('{}R'.format(amount))
            emit('status', {'msg': "You played {}".format(action)})

        new_round = game.search.check_new_round()

        if not new_round:
            action = game.pluribus_action()
            emit('status', {'msg': "Pluribus played {}".format(action)})
            new_round = game.search.check_new_round()
        
        if new_round:
            emit('status', {"msg": "End of round. The state of the game is {}".format(game.search.game_state.public_state)})

        if game.search.terminal:
            payoffs = game.search.game_state.payoff()
            if len(game.search.game_state.winners) > 1:
                emit('status', {'msg': "There was a tie. pot split: {}".format(payoffs)})

            else:
                emit('status', {'msg': 
                "Player {} won. They won {}".format(game.search.game_state.winners[0] + 1, max(payoffs))})
    

if __name__ == '__main__':
    socketio.run(app, debug=True)