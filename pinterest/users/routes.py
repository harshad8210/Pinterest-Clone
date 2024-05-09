from flask import Blueprint, session, render_template, flash, redirect, url_for, request, jsonify
from pinterest.users.form import RegistrationForm, LoginForm, UpdateAccForm, RequestResetForm, ResetPasswordForm
from pinterest.main.form import SearchForm
from pinterest.models import User, Pin, UserInterest, Tags, SavePin, Board, Follow, BlockUser
from pinterest import db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from pinterest.users.utils import selected_user_tags, save_pic, count_follower
from flask_mail import Message
from flask.views import View
from pinterest.msg import user_acc_update_msg, user_logout_msg, user_login_error_msg, user_login_msg, \
    user_pass_update_msg, reset_pass_email_msg, user_access_msg

users = Blueprint('users', __name__)


class LoginPage(View):
    """ user login page route.
    LoginPage:returns
    user login form page, if user is authenticated redirect to home page.
    """

    methods = ['GET', 'POST']

    def dispatch_request(self):
        if current_user.is_authenticated:
            session.permanent = True
            return redirect(url_for('main.home_page'))
        form = LoginForm()

        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            blockuser = BlockUser.query.filter_by(user_id=user.id).first()
            if blockuser is None:
                if user and bcrypt.check_password_hash(user.password, form.password.data):
                    login_user(user, remember=form.remember.data)
                    next_page = request.args.get('next')
                    flash(user_login_msg, 'success')

                    if next_page:
                        return redirect(next_page)
                    else:
                        return redirect(url_for('main.home_page'))
                else:
                    flash(user_login_error_msg, 'danger')
            else:
                flash('You are blocked because ' + blockuser.reason, 'danger')
        return render_template('login.html', title='Login', form=form)


users.add_url_rule('/login', view_func=LoginPage.as_view('login_page'))


@users.route("/register", methods=['POST', 'GET'])
def register_page():
    """ user registration route.
    register_page :return: registration form page,
    if form is validate on submit visitor have new account and redirect to login page.
    """

    if current_user.is_authenticated:
        return redirect(url_for('main.home_page'))
    form = RegistrationForm()
    tags = Tags.query.all()

    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pass)
        db.session.add(user)
        db.session.commit()

        interests_list = request.form.get('interest')
        interests = interests_list.split(",")
        for interest in interests:
            user_interest = UserInterest(user_id=user.id, tag_id=interest)
            db.session.add(user_interest)

        db.session.commit()
        flash(f'Account created for {form.username.data}!!!...', 'success')
        return redirect(url_for('users.login_page'))
    return render_template('register.html', title='Registration', form=form, tags=tags)


@users.route("/profile", methods=['POST', 'GET'])
@login_required
def profile_page():
    """ profile page route,
    :return:all details of logged user and update profile form,
    if form is validate on submit it will update all details of user and redirect to new profile page.
    """

    form = UpdateAccForm()
    tags = Tags.query.all()
    user_save_pins = SavePin.query.filter_by(user_id=current_user.id).all()
    user_tags = UserInterest.query.filter_by(user_id=current_user.id).all()
    followers, following = count_follower(current_user.id)
    selected_tags = selected_user_tags(user_tags)
    pins = Pin.query.filter_by(user_id=current_user.id).all()
    boards = Board.query.filter_by(user_id=current_user.id).all()

    if form.validate_on_submit():
        interests_list = request.form.get('interests')
        interests = interests_list.split(",")
        if form.profile_pic.data:
            profile_name = save_pic(form.profile_pic.data)
            current_user.profile_pic = profile_name

        if selected_tags != interests:
            # for delete interest--------------------
            for selected_tag in selected_tags:
                if selected_tag not in interests:
                    UserInterest.query.filter_by(tag_id=selected_tag, user_id=current_user.id).delete()
                    db.session.commit()

            # for update add new interests------------------------
            if len(interests) != 1:
                for interest_id in interests:
                    if interest_id not in selected_tags:
                        user_interest = UserInterest(user_id=current_user.id, tag_id=interest_id)
                        db.session.add(user_interest)

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash(user_acc_update_msg, 'success')
        return redirect(url_for('users.profile_page'))

    # current user data------------------------------------------
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    profile_pic = url_for('static', filename='profile_img/' + current_user.profile_pic)
    return render_template('profile.html', title='profile', form=form, profile_pic=profile_pic, tags=tags,
                           selected_tags=selected_tags, pins=pins, user_save_pins=user_save_pins, boards=boards,
                           followers=followers, following=following)


@users.route("/profile/<int:user_id>/followers")
@login_required
def user_followers_list(user_id):
    """user follower list
    :param user_id: integer
    :return: followers list to the template
    """

    if user_id == current_user.id:
        form = SearchForm()
        followers = Follow.query.filter_by(user_id=user_id).order_by(Follow.id.desc()).all()
        if followers == [None]:
            flash('You have no Followers.', 'info')
            return redirect(url_for('users.profile_page'))
        return render_template('user_followers.html', followers=followers, form=form)
    flash(user_access_msg, 'warning')
    return redirect(url_for('users.profile_page'))


@users.route("/profile/<int:user_id>/following")
@login_required
def user_followings_list(user_id):
    """user following list
    :param user_id: integer
    :return: following list to the template
    """

    if user_id == current_user.id:
        form = SearchForm()
        followings = Follow.query.filter_by(follower_id=user_id).order_by(Follow.id.desc()).all()
        if followings == [None]:
            flash('You are not following anyone.', 'info')
            return redirect(url_for('users.profile_page'))
        return render_template('user_following.html', followings=followings, form=form)
    flash(user_access_msg, 'warning')
    return redirect(url_for('users.profile_page'))


@users.route("/logout")
def logout():
    """ logout route
    :return: redirect to home page after logged out.
    """

    logout_user()
    flash(user_logout_msg, 'success')
    return redirect(url_for('main.home_page'))


@users.route("/profile/<string:username>")
def user_profile(username):
    """ user profile route
    :param username:
    :return: show selected user profile and logged user can follow and unfollow profile user.
    """

    form = SearchForm()
    user_pro = User.query.filter_by(username=username).first()
    followers, following = count_follower(user_pro.id)
    pins = Pin.query.filter_by(user_id=user_pro.id).all()
    boards = Board.query.filter_by(user_id=user_pro.id).all()
    profile_pic = url_for('static', filename='profile_img/' + user_pro.profile_pic)
    return render_template('user_profile.html', title=username, user=user_pro, profile_pic=profile_pic, pins=pins,
                           form=form, followers=followers, following=following, boards=boards)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='inexture@gmail.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@users.route("/reset_password", methods=['POST', 'GET'])
def reset_request():
    """ reset password route
    :return: sent a mail to user email with token link
    """

    if current_user.is_authenticated:
        return redirect(url_for('main.home_page'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash(reset_pass_email_msg, 'info')
        return redirect(url_for('users.login_page'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['POST', 'GET'])
def reset_token(token):
    """ reset password route
    :param token: string
    :return: redirect to reset password form
    """

    if current_user.is_authenticated:
        return redirect(url_for('main.home_page'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pass
        db.session.commit()
        flash(user_pass_update_msg, 'success')
        return redirect(url_for('users.login_page'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@users.route('/user/follow/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    """follow unfollow user route.
    """

    if request.method == "POST":

        follower = Follow.query.filter_by(user_id=user_id, follower_id=current_user.id).first()
        response = {}
        if follower:
            db.session.delete(follower)
            db.session.commit()
            response['follower'] = False
        else:
            follower = Follow(user_id=user_id, follower_id=current_user.id)
            db.session.add(follower)
            db.session.commit()
            response['follower'] = True

        follower_count = Follow.query.filter_by(user_id=user_id).count()
        response['follower_count'] = follower_count

        return jsonify(response)
    else:
        return redirect(url_for('main.home_page'))
