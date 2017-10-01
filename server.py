import bottle
from genetic import GA


ga = GA()
app = bottle.Bottle()


@app.get('/')
def home():
    data = ga.get_data()
    return bottle.template('home.html', **data)


@app.get('/mark-hit/<ident>')
def mark_hit(ident):
    ga.mark_hit(ident)


if __name__ == '__main__':
    app.run(debug=True)
