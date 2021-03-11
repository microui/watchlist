from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from os import path


app = Flask(__name__)
login_manager = LoginManager(app)
# 访问了设置登录保护的页面时，会自动跳转到登录页，需手动设置登录也的视图端点，不然会报错
login_manager.login_view = 'login'
# login_manager.login_message = '自定义错误提示'
app.secret_key = '123456'
db = SQLAlchemy(app)

prefix = r'sqlite:///'
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + path.join(app.root_path, 'data.db')
# 关闭对模型修改的监控
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    from watchlist.models import User
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象


# 模板上下文处理函数
@app.context_processor
def inject_user():
    from watchlist.models import User
    return dict(user=current_user)


from watchlist import commands, errors, models, views
