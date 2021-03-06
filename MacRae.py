from flask import Flask, render_template, request, redirect, url_for, session
import config
from models import User, Question, Answer, UserInfo
from extra import db
from decorators import login_required


app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)


@app.route('/')
def men():
    return render_template('men.html')


@app.route('/home/')
def index():
    content = {
        'questions': Question.query.order_by('create_time').all()
    }
    return render_template('index.html', **content)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        user = User.query.filter(User.telephone == telephone, User.password == password).first()
        if user:
            # 登录成功 设置Cookie
            session['user_id'] = user.id
            session.permanent = True
            print('登录成功')
            return redirect(url_for('index'))
        else:
            return '手机号或密码错误'


@login_required
@app.route('/logout/')
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))


@app.context_processor
def my_context_processor():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return {'user': user}
    return {}


@app.route('/question/', methods=['GET', 'POST'])
@login_required
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        # 写入数据库
        title = request.form.get('title')
        content = request.form.get('content')
        question = Question(title=title, content=content)
        user_id = session.get('user_id')  # 获取id
        user = User.query.filter(User.id == user_id).first()
        question.author = user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('index'))


@login_required
@app.route('/detail/<question_id>')
def detail(question_id):
    question_model = Question.query.filter(Question.id == question_id).first()
    number_answer = len(question_model.answers)
    return render_template('detail.html', question_model=question_model, number_answer=number_answer)


@app.route('/regist/', methods=['GET', 'POST'])
def regist():
    if request.method == 'GET':
        return render_template('regist.html')
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        # 手机号不能重复
        user = User.query.filter(User.telephone == telephone).first()
        if user:
            print('手机号已被注册')

            return '手机号已被注册'
        else:
            if password != repassword:
                print('两次密码输入不一致')
                return '两次密码输入不一致'
            else:
                print('注册成功')
                user = User(telephone=telephone, username=username, password=password)
                db.session.add(user)
                db.session.commit()
                # 注册成功页面跳转到登录界面
                return redirect(url_for('login'))


@app.route('/add_answer/', methods=['POST'])
@login_required
def add_answer():
    content = request.form.get('answer_content')
    answer = Answer(content=content)
    user_id = session['user_id']
    question_id = request.form.get('question_id')
    user = User.query.filter(User.id == user_id).first()
    question = Question.query.filter(Question.id == question_id).first()
    answer.author = user
    answer.question = question
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('detail', question_id=question_id))


@app.route('/user/', methods=['get', 'post'])
@login_required
def user():
    if request.method == 'GET':
        user_info = UserInfo.query.filter(User.id == session['user_id']).first()
        print(user_info)
        return render_template('user.html', user_info=user_info)

    else:
        signature = request.form.get('signature')
        birthday = request.form.get('birthday')
        user_id = session['user_id']
        user_info = UserInfo.query.filter(User.id == session['user_id']).first()
        if user_info:
            db.session.delete(user_info)
            user_info = UserInfo(signature=signature, birthday=birthday, user_id=user_id)
            db.session.add(user_info)
            db.session.commit()
        else:
            user_info = UserInfo(signature=signature, birthday=birthday, user_id=user_id)
            db.session.add(user_info)
            db.session.commit()
        print(user_info.signature)
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)