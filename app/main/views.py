from flask import render_template, redirect,url_for,abort,request
from . import main
from flask_login import login_required,current_user
from ..models import User,Note,Subscriber
from ..import db, photos
import secrets
import os
from PIL import Image
from .forms import UpdateProfile,CreateNote
from ..email import mail_message

@main.route('/profile/<username>')
@login_required
def profile(username):

    '''
    View profile page function that returns the profile details of the current user logged in
    '''
    user = User.query.filter_by(username = username).first()
    
    if user is None:
        abort(404)
 
    return render_template("profile/profile.html", user = user)     
    

@main.route('/profile/<username>/update',methods = ['GET','POST'])
@login_required
def update_profile(username):
    user = User.query.filter_by(username = username).first()
    if user is None:
        abort(404)

    form = UpdateProfile()

    if form.validate_on_submit():
        user.bio = form.bio.data
        db.session.add(user)
        db.session.commit()

        flash('User bio updated')

        return redirect(url_for('main.profile',username=user.username))

    return render_template('profile/update.html',user=user,form =form)    

@main.route('/profile/<username>/update/pic',methods= ['POST'])
@login_required
def update_pic(username):
    user = User.query.filter_by(username = username).first()
    if 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        path = f'photos/{filename}'
        user.profile_pic_path = path
        db.session.commit()

        flash('User pic updated')
        
    return redirect(url_for('main.update_profile',username=username))


#Views
@main.route('/')
def index():
    notes = Note.query.order_by(Note.time.desc())
    return render_template('notes_page.html', notes=notes)

@main.route('/new_note', methods=['POST','GET'])
@login_required
def new_note():
    subscribers = Subscriber.query.all()
    form = CreateNote()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        user_id =  current_user._get_current_object().id
        note = Note(title=title, content=content,user_id=user_id)
        note.save()
        for subscriber in subscribers:
            mail_message("New note created","email/new_note",subscriber.email,note=note)
        return redirect(url_for('main.index'))
    return render_template('add_note.html', form = form)
