from flask import Flask, escape, url_for
app = Flask(__name__)

@app.route('/')
def root():
    return 'hello'


@app.route('/home')
def home():
    return u'wellcome 欢迎'


@app.route('/home/<name>')
def detail(name):
    return 'User: %s' % escape(name)


@app.route('/test')
def test_url_for():
    print(url_for('home'))
    print(url_for('root'))
    print(url_for('detail', name='lily'))
    return 'test page'
