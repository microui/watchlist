from flask import request, redirect, url_for, flash, render_template
from flask_login import current_user, logout_user, login_user, login_required

from watchlist import app, db

from watchlist.models import Movie, User, Article


def column_name_list(cls):
    column_collection_str_list = cls.__table__.__dict__['columns'].__str__().split("'")
    column_list = []
    for a in range(0, len(column_collection_str_list)):
        if a % 2 != 0:
            column_list.append(column_collection_str_list[a].split('.')[1])
    return column_list


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
        print('username', username)
        # 验证数据
        if not username or not password:
            flash('Invalid login.')  # 显示错误提示
            return redirect(url_for('login'))  # 重定向回主页
        user = User.query.filter(User.username == username).first()
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


@app.route('/article/list', methods=['GET', 'POST'])
def article():
    # form提交
    if not current_user.is_authenticated:
        flash('请先登录')
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = dict(request.form)
        print('current_user', current_user.__dict__)
        dict_target = {}
        for key, val in data.items():
            if key in column_name_list(Article):
                dict_target[key] = val
        record = Article(**dict_target)
        record.author_id = current_user.__getattr__('id')
        db.session.add(record)
        db.session.commit()
        return redirect(url_for('article'))
    article_list = Article.query.all()
    return render_template('article.html', article=article_list)


@app.route('/article/findByUser', methods=['GET'])
def article_search():
    # form提交
    if not current_user.is_authenticated:
        flash('请先登录')
        return redirect(url_for('login'))
    data = request.args.get('keyword')
    if data:
        user = User.query.filter(User.username == data).first()
        if user is None:
            return render_template('article.html', article=[])
        return render_template('article.html', article=user.article)
    filter_list = Article.query.all()
    return render_template('article.html', article=filter_list)


@app.route('/article/delete/<int:article_id>', methods=['POST'])
@login_required
def article_delete(article_id):
    print('article_id', article_id)
    record = Article.query.get_or_404(article_id)
    db.session.delete(record)
    db.session.commit()  # 提交数据库会话
    flash('Item delete.')  # 显示成功创建的提示
    return redirect(url_for('article'))  # 重定向回主页


@app.route('/user/list')
def user_list():
    users = User.query.all()
    print('users', users)
    for user in users:
        print(user.article)
    return render_template('user.html', users=users)


@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    user = User.query.first()
    return render_template('errors/404.html')  # 返回模板和状态码