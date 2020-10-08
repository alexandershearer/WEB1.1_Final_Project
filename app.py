from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

#Setup pymongo DB
app.config["MONGO_URI"] = "mongodb://localhost:27017/gamesDatabase"
mongo = PyMongo(app)

#My home page with games
@app.route('/')
def games_list():

    games_info = mongo.db.games.find()

    context = {
        'games': games_info,
    }
    return render_template('games_list.html', **context)

@app.route('/about')
def about():
    return render_template('about.html')

#Make the create function in order to add games to the library
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        game_name = request.form.get('game_name')
        
        new_game = {
            'name': game_name,
            'genre': request.form.get('genre'),
            'cover_url': request.form.get('cover'),
            'date_played': request.form.get('date_played')
        }

        result = mongo.db.games.insert_one(new_game)
        return redirect(url_for('detail', game_id=result.inserted_id))

    else:
        return render_template('create.html')    

#The viewing page for a specific game for when you add it and when you want to edit it
@app.route('/game/<game_id>')
def detail(game_id):
    display_game = mongo.db.games.find_one({'_id': ObjectId(game_id)})

    sessions = mongo.db.sessions.find()

    context = {
        'game': display_game,
        'sessions': sessions
    }

    return render_template('detail.html', **context)

#Creating and logging new sessions for your games
@app.route('/session/<game_id>', methods=['POST'])
def session(game_id):
    new_session = {
        'hours': request.form.get('session_time'),
        'date': request.form.get('date_played'),
        'game_id': ObjectId(game_id)
    }

    mongo.db.sessions.insert_one(new_session)

    return redirect(url_for('detail', game_id=game_id))


@app.route('/edit/<game_id>', methods=['GET', 'POST'])
def edit(game_id):
    if request.method == 'POST':
        mongo.db.game.update_one(
            {'_id': ObjectId(game_id)},
            {
                '$set': {
                    'name': request.form.get('game_name'),
                    'genre': request.form.get('genre'),
                    'cover_url': request.form.get('cover'),
                    'date': request.form.get('date_played')
                }
            }
        )

        return redirect(url_for('detail', game_id=game_id))
    else:
        display_game = mongo.db.games.find_one({'_id': ObjectId(game_id)})

        context = {
            'game': display_game
        }

        return render_template('edit.html', **context)
    
@app.route('/delete/<game_id>', methods=['POST'])
def delete(game_id):

    mongo.db.games.delete_one({ '_id': ObjectId(game_id) })
    mongo.db.sessions.delete_many({ 'game_id': ObjectId(game_id)})
    
    return redirect(url_for('games_list'))

if __name__ == '__main__':
    app.run(debug=True)