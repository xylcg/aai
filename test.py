import pytest
from app import app, db, User, Chat, Message
from datetime import datetime
import uuid


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_register(client):
    """
    测试用户注册功能
    步骤：
    1. 发送注册请求，包含用户名和密码
    2. 检查响应中是否包含注册成功的提示信息
    3. 检查数据库中是否成功创建了新用户
    """
    response = client.post('/register', data=dict(
        username='testuser',
        password='testpassword'
    ), follow_redirects=True)
    assert b'注册成功，请登录' in response.data
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user is not None


def test_login(client):
    """
    测试用户登录功能
    步骤：
    1. 先注册一个用户
    2. 发送登录请求，使用注册的用户名和密码
    3. 检查响应中是否包含个人中心页面的提示信息
    """
    # 先注册用户
    client.post('/register', data=dict(
        username='testuser',
        password='testpassword'
    ))
    response = client.post('/login', data=dict(
        username='testuser',
        password='testpassword'
    ), follow_redirects=True)
    assert b'个人中心' in response.data


def test_logout(client):
    """
    测试用户退出功能
    步骤：
    1. 先注册并登录一个用户
    2. 发送退出请求
    3. 检查响应中是否包含登录页面的提示信息
    """
    # 先注册并登录用户
    client.post('/register', data=dict(
        username='testuser',
        password='testpassword'
    ))
    client.post('/login', data=dict(
        username='testuser',
        password='testpassword'
    ))
    response = client.get('/logout', follow_redirects=True)
    assert b'登录' in response.data


def test_chat(client):
    """
    测试聊天功能
    步骤：
    1. 先注册并登录一个用户
    2. 发送聊天请求，包含聊天提示信息
    3. 检查响应状态码是否为 200
    4. 检查数据库中是否成功保存了聊天记录
    """
    # 先注册并登录用户
    client.post('/register', data=dict(
        username='testuser',
        password='testpassword'
    ))
    client.post('/login', data=dict(
        username='testuser',
        password='testpassword'
    ))
    response = client.post('/chat', data=dict(
        prompt='测试聊天'
    ), follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        chat = Chat.query.filter_by(user=user).first()
        assert chat is not None


def test_delete_chat(client):
    """
    测试删除聊天记录功能
    步骤：
    1. 先注册并登录一个用户
    2. 创建一个聊天记录
    3. 发送删除聊天记录请求
    4. 检查响应状态码是否为 200
    5. 检查数据库中相应的聊天记录是否已删除
    """
    # 先注册并登录用户
    client.post('/register', data=dict(
        username='testuser',
        password='testpassword'
    ))
    client.post('/login', data=dict(
        username='testuser',
        password='testpassword'
    ))
    # 创建一个聊天记录
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        chat_id = str(uuid.uuid4())
        chat = Chat(id=chat_id, title='Test Chat', user=user)
        db.session.add(chat)
        db.session.commit()
    response = client.post(f'/delete_chat/{chat_id}', follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        chat = Chat.query.filter_by(id=chat_id).first()
        assert chat is None
