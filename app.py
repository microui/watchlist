from flask import Flask, escape, url_for, render_template, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from os import path
from werkzeug.security import generate_password_hash, check_password_hash
import click
from flask_login import UserMixin


app = Flask(__name__)
login_manager = LoginManager(app)

# 访问了设置登录保护的页面时，会自动跳转到登录页，需手动设置登录也的视图端点，不然会报错
login_manager.login_view = 'login'
# login_manager.login_message = '自定义错误提示'
app.secret_key = '123456'

db = SQLAlchemy(app)

prefix = r'sqlite:///'
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控


# 注册为命令
@app.cli.command()
# 设置选项
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息


# 注册为命令
@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()

    # 全局的两个变量移动到这个函数内
    name = 'Grey Li'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')


@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    db.create_all()
    user = User.query.first()
    if user is not None:
        user.username = username
        user.set_password(password)
    else:
        user = User(username=username, name='admin')
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    click.echo('Done')


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':  # 判断是否是 POST 请求
        if not current_user.is_authenticated:
            flash('请先登录')
            return redirect(url_for('index'))
        # 获取表单数据
        title = request.form.get('title')  # 传入表单对应输入字段的 name 值
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')  # 显示错误提示
            return redirect(url_for('index'))  # 重定向回主页
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year)  # 创建记录
        db.session.add(movie)  # 添加到数据库会话
        db.session.commit()  # 提交数据库会话
        flash('Item created.')  # 显示成功创建的提示
        return redirect(url_for('index'))  # 重定向回主页
    movie = Movie.query.all()
    return render_template('index_in_base.html', movie=movie)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # 判断是否是 POST 请求
        # 获取表单数据
        username = request.form.get('username')  # 传入表单对应输入字段的 name 值
        password = request.form.get('password')
        # 验证数据
        if not username or not password:
            flash('Invalid login.')  # 显示错误提示
            return redirect(url_for('login'))  # 重定向回主页
        user = User.query.first()
        print('user--->', user)
        if user.username == username and user.validate_password(password):
            login_user(user)
            flash('login success')
            return redirect(url_for('index'))
        flash('Invalid login')
        return redirect(url_for('login'))  # 重定向回主页
    return render_template('login.html')  # 重定向回主页


@app.route('/setting', methods=['GET', 'POST'])
@login_required
def setting():
    if request.method == 'POST':  # 判断是否是 POST 请求
        # 获取表单数据
        name = request.form.get('name')  # 传入表单对应输入字段的 name 值
        # 验证数据
        if not name or len(name) > 60:
            flash('Invalid name.')  # 显示错误提示
            return redirect(url_for('setting'))  # 重定向回主页
        current_user.username = name
        db.session.commit()
        flash('setting success')
        return redirect(url_for('index'))
        flash('Invalid login')
        return redirect(url_for('index'))  # 重定向回主页
    return render_template('setting.html')  # 重定向回主页


@app.route('/logout')
def logout():
    logout_user()
    print('ccc',current_user)
    flash('Goobye')
    return redirect(url_for('index'))


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required  # 设置登录保护
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if request.method == 'POST':  # 判断是否是 POST 请求
        # 获取表单数据
        title = request.form.get('title')  # 传入表单对应输入字段的 name 值
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')  # 显示错误提示
            return redirect(url_for('edit', movie_id=movie_id))  # 重定向回主页
        # 保存表单数据到数据库
        movie.title = title
        movie.year = year
        db.session.commit()  # 提交数据库会话
        flash('Item updated.')  # 显示成功创建的提示
        return redirect(url_for('edit', movie_id=movie.id))  # 重定向回主页

    return render_template('edit.html', movie=movie)


@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()  # 提交数据库会话
    flash('Item delete.')  # 显示成功创建的提示
    return redirect(url_for('index'))  # 重定向回主页


@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    user = User.query.first()
    return render_template('404_in_base.html')  # 返回模板和状态码


# 模板上下文处理函数
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)
