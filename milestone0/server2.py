from flask import Flask, render_template, request, redirect, url_for, session
import requests
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'
filename = 'mock_user_data.json'

ALPHA_VANTAGE_API_KEY = 'ZBD3QIPITMQNSPPF'

def write_to_file(data):
    with open(filename, 'w') as file:
        json.dump(data, file)

# Mock user data (you would replace this with a database)
users = {
    'user1': {'password': 'password1', 'portfolio': ['AAPL', 'GOOG']},
    'user2': {'password': 'password2', 'portfolio': ['MSFT', 'AMZN']}
}

def get_stock_data(symbol):
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    print(data)  # Temporarily print data for debugging

    return data

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('portfolio'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

def add_symbol_to_portfolio(username, symbol):
    if symbol not in users[username]['portfolio']:
        users[username]['portfolio'].append(symbol)
        write_to_file(users)

def remove_symbol_from_portfolio(username, symbol):
    if symbol in users[username]['portfolio']:
        users[username]['portfolio'].remove(symbol)
        write_to_file(users)

@app.route('/add_symbol', methods=['POST'])
def add_symbol_route():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    symbol = request.form['symbol'].upper()
    add_symbol_to_portfolio(username, symbol)
    return redirect(url_for('portfolio'))

@app.route('/remove_symbol', methods=['POST'])
def remove_symbol_route():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    symbol = request.form['symbol'].upper()
    remove_symbol_from_portfolio(username, symbol)
    return redirect(url_for('portfolio'))

@app.route('/portfolio')
def portfolio():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    portfolio = users[username]['portfolio']
    portfolio_data = {}
    total_value = 0
    for symbol in portfolio:
        stock_data = get_stock_data(symbol)
        if 'Global Quote' in stock_data and '05. price' in stock_data['Global Quote']:
            price = float(stock_data['Global Quote']['05. price'])
            portfolio_data[symbol] = stock_data
            total_value += price
        else:
            portfolio_data[symbol] = {'Global Quote': {'05. price': 'N/A'}}
    return render_template('portfolio.html', portfolio_data=portfolio_data, total_value=total_value)

@app.route('/search', methods=['POST'])
def search():
    if 'username' not in session:
        return redirect(url_for('login'))
    symbol = request.form['symbol'].upper()
    stock_data = get_stock_data(symbol)
    return render_template('stock_detail.html', stock_data=stock_data)

@app.route('/all_stocks')
def all_stocks():
    return render_template('all_stocks.html')

@app.route('/{symbol}')
def stock_detail(symbol):
    stock_data = get_stock_data(symbol)
    return render_template('stock_detail.html', stock_data=stock_data)

if __name__ == '__main__':
    app.run(debug=True)