from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, date
from models import db, Photo, Message, Event
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')  # 从环境变量获取密钥

# 数据库配置
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    # Heroku 数据库 URL 修复
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    # 计算在一起的天数
    start_date = datetime(2021, 7, 21)
    today = datetime.now()
    days_together = (today - start_date).days

    return render_template('index.html', days=days_together)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/upload_photo', methods=['GET', 'POST'])
def upload_photo():
    if request.method == 'POST':
        if 'photo' not in request.files:
            flash('没有选择文件')
            return redirect(request.url)
        
        file = request.files['photo']
        if file.filename == '':
            flash('没有选择文件')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            photo = Photo(
                filename=filename,
                description=request.form.get('description', '')
            )
            db.session.add(photo)
            db.session.commit()
            
            flash('照片上传成功！')
            return redirect(url_for('photos'))
    
    return render_template('upload_photo.html')

@app.route('/photos')
def photos():
    photos = Photo.query.order_by(Photo.upload_date.desc()).all()
    return render_template('photos.html', photos=photos)

@app.route('/photos/delete/<int:photo_id>', methods=['POST'])
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    
    # 删除文件系统中的照片文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # 从数据库中删除记录
    db.session.delete(photo)
    db.session.commit()
    
    flash('照片已删除！')
    return redirect(url_for('photos'))

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'POST':
        content = request.form.get('content')
        
        if content:
            message = Message(content=content, author="才睡醒")
            db.session.add(message)
            db.session.commit()
            flash('留言发布成功！')
            return redirect(url_for('messages'))
    
    messages = Message.query.order_by(Message.created_at.desc()).all()
    return render_template('messages.html', messages=messages)

@app.route('/messages/edit/<int:message_id>', methods=['GET', 'POST'])
def edit_message(message_id):
    message = Message.query.get_or_404(message_id)
    
    if request.method == 'POST':
        content = request.form.get('content')
        
        if content:
            message.content = content
            message.author = "才睡醒"  # 保持作者名称一致
            message.created_at = datetime.utcnow()  # 更新时间
            db.session.commit()
            flash('留言修改成功！')
            return redirect(url_for('messages'))
    
    return render_template('edit_message.html', message=message)

@app.route('/messages/delete/<int:message_id>', methods=['POST'])
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    flash('留言已删除！')
    return redirect(url_for('messages'))

@app.route('/events', methods=['GET', 'POST'])
def events():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        
        if title and start_date and end_date:
            event = Event(
                title=title,
                description=description,
                start_date=start_date,
                end_date=end_date
            )
            db.session.add(event)
            db.session.commit()
            flash('应援活动创建成功！')
            return redirect(url_for('events'))
    
    events = Event.query.order_by(Event.start_date.desc()).all()
    return render_template('events.html', events=events)

if __name__ == '__main__':
    app.run(debug=True)