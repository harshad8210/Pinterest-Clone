from flask import Blueprint, render_template, send_file, flash, redirect, url_for, request, abort, jsonify
from flask.views import View
from flask_login import current_user, login_required
from sqlalchemy import func

from pinterest.main.form import SearchForm
from pinterest.pins.form import NewPostForm, UpdatePostForm, NewBoardForm
from pinterest.models import User, Pin, Tags, SavePin, Board, SavePinBoard, Like, PinTags, Comment
from pinterest import db
from pinterest.pins.utils import save_pin_img, get_selected_tags, list_tag_trandings
from pinterest.msg import pin_create_msg, pin_update_msg, pin_delete_msg, pin_saved_msg, pin_save_msg, pin_unsave_msg, \
    board_create_msg, board_update_msg, board_delete_msg, board_save_pin_msg, board_saved_pin_msg, board_not_exist_msg, \
    board_empty_msg, board_remove_pin_msg, pin_not_exist_msg, pin_empty_comment_msg, pin_comment_not_exist_msg, \
    pin_comment_access_msg, admin_access_msg

pins = Blueprint('pins', __name__)


class NewPin(View):
    """ New pin route
    :returns redirect to new pin form ,
    if form is validate on submit it's creates new pin and redirect to home page.
    """

    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self):
        form = NewPostForm()
        all_tags = Tags.query.all()

        """get count of each tag, which is used in pins
            for finding out tranding tags
        """
        tranding_tags_dict = db.session.query(func.count(PinTags.tag_id), PinTags.tag_id).group_by(PinTags.tag_id).all()

        tags = list_tag_trandings(all_tags, tranding_tags_dict)
        if form.validate_on_submit():
            if form.post_img.data:
                pin_pic = save_pin_img(form.post_img.data)
                privacy = request.form.get('options-pin')
                pin = Pin(title=form.title.data, pin_pic=pin_pic, content=form.content.data, user_id=current_user.id,
                          privacy=privacy)
                db.session.add(pin)
                db.session.commit()

                pin_tag_list = request.form.get('img_tag')
                pin_tags = pin_tag_list.split(",")

                for tag in pin_tags:
                    pin_tag = PinTags(pin_id=pin.id, tag_id=tag)
                    db.session.add(pin_tag)

                db.session.commit()
                flash(pin_create_msg, 'success')
                return redirect(url_for('main.home_page'))
        return render_template('new_post.html', title='New Post', form=form, tags=tags, all_tags=all_tags)


pins.add_url_rule('/pin/new', view_func=NewPin.as_view('new_pin'))


class SelectedPin(View):
    """ selected pin route,
    :returns all the details of pin.
    """

    decorators = [login_required]

    def dispatch_request(self, pin_id=None):
        form = SearchForm()
        pin = Pin.query.get_or_404(pin_id)
        comments = Comment.query.filter_by(pin_id=pin_id).order_by(Comment.id.desc()).all()
        user = User.query.get_or_404(pin.user_id)
        boards = Board.query.filter_by(user_id=current_user.id).all()
        return render_template('pin.html', title=pin.title, pin=pin, pin_id=pin_id, user=user, boards=boards, form=form,
                               comments=comments)


pins.add_url_rule('/pin/<int:pin_id>', view_func=SelectedPin.as_view('selected_pin'))


class UpdatePin(View):
    """ update pin route
    :param: pin_id
    :returns redirect to update pin form,
    if form is validate on submit redirect to new updated form.
    """

    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self, pin_id=None):
        pin = Pin.query.get_or_404(pin_id)
        user = User.query.get_or_404(pin.user_id)
        pin_tags = PinTags.query.filter_by(pin_id=pin_id).all()
        selected_pin_tag = get_selected_tags(pin_tags)
        form = UpdatePostForm()
        tags = Tags.query.all()
        if pin.author != current_user:
            abort(403)
        if form.validate_on_submit():
            privacy = request.form.get('options-pin-update')
            pin.title = form.title.data
            pin.content = form.content.data
            pin.privacy = privacy

            new_tags_list = request.form.get('img_tag')
            new_tags = new_tags_list.split(",")

            if selected_pin_tag != new_tags:
                # for delete pin tag--------------------
                for selected_tag in selected_pin_tag:
                    if selected_tag not in new_tags:
                        PinTags.query.filter_by(tag_id=selected_tag, pin_id=pin_id).delete()
                        db.session.commit()

                # for update add new pin tag------------------------

                for interest_id in new_tags:
                    if interest_id not in selected_pin_tag:
                        pin_new_tag = PinTags(pin_id=pin_id, tag_id=interest_id)
                        db.session.add(pin_new_tag)
                        db.session.commit()

            flash(pin_update_msg, 'success')
            return redirect(url_for('pins.update_pin', pin_id=pin.id))
        if request.method == 'GET':
            form.title.data = pin.title
            form.content.data = pin.content

        return render_template('update_pin.html', title=pin.title, pin=pin, user=user, form=form,
                               selected_pin_tag=selected_pin_tag, tags=tags)


pins.add_url_rule("/pin/<int:pin_id>/update", view_func=UpdatePin.as_view('update_pin'))


class DeletePin(View):
    """
    delete pin route.
    """

    methods = ['POST']
    decorators = [login_required]

    def dispatch_request(self, pin_id=None):
        pin = Pin.query.get_or_404(pin_id)
        if pin.author != current_user:
            abort(403)
        db.session.delete(pin)
        db.session.commit()
        flash(pin_delete_msg, 'success')
        return redirect(url_for('users.profile_page'))


pins.add_url_rule('/pin/<int:pin_id>/delete', view_func=DeletePin.as_view('delete_pin'))


class UserSavePin(View):
    """ save pin to the profile route
    """

    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self, pin_id=None):
        pin = SavePin.query.filter_by(pin_id=pin_id).first()
        if pin is None:
            save_pin = SavePin(user_id=current_user.id, pin_id=pin_id)
            db.session.add(save_pin)
            db.session.commit()
            flash(pin_save_msg, 'success')
            return redirect(url_for('users.profile_page'))
        else:
            flash(pin_saved_msg, 'info')
            return redirect(url_for('users.profile_page'))


pins.add_url_rule('/pin/<int:pin_id>/save', view_func=UserSavePin.as_view('save_pin'))


# Un-save pin by user----------------------------------------
class UserUnSavePin(View):
    """
    unsave pin from the profile route.
    """

    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self, pin_id=None):
        """unsave pin
        :param pin_id:'int'
        :return: user profile page
        """

        pin = Pin.query.get_or_404(pin_id)
        SavePin.query.filter_by(user_id=current_user.id, pin_id=pin_id).delete()
        db.session.commit()
        flash(pin_unsave_msg, 'success')
        return redirect(url_for('users.profile_page'))


pins.add_url_rule('/pin/<int:pin_id>/unsave', view_func=UserUnSavePin.as_view('unsave_pin'))


# create new board-------------------------------------------------
class NewBoard(View):
    """create new board route
    """

    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self):
        form = NewBoardForm()
        user_save_pins = SavePin.query.filter_by(user_id=current_user.id).all()

        if form.validate_on_submit():
            privacy = request.form.get('options-board')
            print(f'{privacy}')
            board = Board(user_id=current_user.id, name=form.name.data, privacy=privacy)
            db.session.add(board)
            db.session.commit()
            flash(board_create_msg, 'success')
            return redirect(url_for('users.profile_page'))

        return render_template('new_board.html', form=form, user_save_pins=user_save_pins)


pins.add_url_rule('/board/new', view_func=NewBoard.as_view('new_board'))


class SavePinToBoard(View):
    """save particulate pin to the board.
    """

    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self, board_id=None, pin_id=None):
        board = SavePinBoard.query.filter_by(board_id=board_id, pin_id=pin_id).first()
        saved_pin = SavePin.query.filter_by(user_id=current_user.id, pin_id=pin_id).first()
        if board is None:
            pin_save_to_board = SavePinBoard(board_id=board_id, pin_id=pin_id)
            if saved_pin is None:
                save_pin = SavePin(user_id=current_user.id, pin_id=pin_id)
                db.session.add(save_pin)
            db.session.add(pin_save_to_board)
            db.session.commit()
            flash(board_save_pin_msg, 'success')
            return redirect(url_for('users.profile_page'))
        else:
            flash(board_saved_pin_msg, 'info')
            return redirect(url_for('users.profile_page'))


pins.add_url_rule('/board/<int:board_id>/save/<int:pin_id>', view_func=SavePinToBoard.as_view('save_pin_board'))


class BoardInfo(View):
    """board information route
    :returns all details of board.
    """

    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self, board_id=None):
        form = SearchForm()
        board_name = Board.query.filter_by(id=board_id).first()
        if board_name.user_id == current_user.id:
            board = SavePinBoard.query.filter_by(board_id=board_id).all()
            if board_name is not None:
                if not board:
                    flash(board_empty_msg, 'info')
                    return render_template('board_details.html', board_name=board_name, board=board, form=form)
                else:
                    return render_template('board_details.html', board_name=board_name, board=board, form=form)
            else:
                flash(board_not_exist_msg, 'warning')
                return redirect(url_for('users.profile_page'))
        else:
            flash(admin_access_msg, 'warning')
            return redirect(url_for('users.profile_page'))


pins.add_url_rule('/board/<int:board_id>', view_func=BoardInfo.as_view('board_info'))


class UserBoardInfo(View):
    """board information route
    :returns all details of board.
    """

    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self, board_id=None):
        form = SearchForm()
        board_name = Board.query.filter_by(id=board_id).first()

        board = SavePinBoard.query.filter_by(board_id=board_id).all()
        if board_name is not None:
            if not board:
                flash(board_empty_msg, 'info')
                return render_template('user_board_details.html', board_name=board_name, board=board, form=form)
            else:
                return render_template('user_board_details.html', board_name=board_name, board=board, form=form)
        else:
            flash(board_not_exist_msg, 'warning')
            return redirect(url_for('users.profile_page'))


pins.add_url_rule('/user/board/<int:board_id>', view_func=UserBoardInfo.as_view('user_board_info'))


class RemovePinBoard(View):
    """remove pins from the board."""

    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self, pin_id=None, board_id=None):
        SavePinBoard.query.filter_by(pin_id=pin_id, board_id=board_id).delete()
        db.session.commit()
        flash(board_remove_pin_msg, 'success')
        return redirect(url_for('pins.board_info', board_id=board_id))


pins.add_url_rule('/board/<int:board_id>/<int:pin_id>/remove', view_func=RemovePinBoard.as_view('remove_pin_board'))


class EditBoard(View):
    """ update board route.
    """

    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self, board_id=None):
        form = NewBoardForm()
        board = Board.query.filter_by(id=board_id, user_id=current_user.id).first()
        if board is not None:
            privacy = request.form.get('options-board-e')
            if form.validate_on_submit():
                board.name = form.name.data
                board.privacy = privacy
                db.session.commit()
                flash(board_update_msg, 'success')
                return redirect(url_for('users.profile_page'))

        if request.method == 'GET':
            form.name.data = board.name
            return render_template('edit_board.html', form=form)

        flash(board_not_exist_msg, 'warning')
        return redirect(url_for('users.profile_page'))


pins.add_url_rule('/board/<int:board_id>/edit', view_func=EditBoard.as_view('edit_board'))


class DeleteBoard(View):
    """delete board route.
    """

    methods = ['GET', 'POST']
    decorators = [login_required]

    def dispatch_request(self, board_id=None):
        SavePinBoard.query.filter_by(board_id=board_id).delete()
        Board.query.filter_by(id=board_id, user_id=current_user.id).delete()
        db.session.commit()
        flash(board_delete_msg, 'success')
        return redirect(url_for('users.profile_page'))


pins.add_url_rule('/board/<int:board_id>/delete', view_func=DeleteBoard.as_view('delete_board'))


@pins.route('/pin/<int:pin_id>/like', methods=['GET', 'POST'])
def like_action(pin_id):
    """like pin route
        :returns redirect to selected pin page,
        if user is already like the pin then they can dislike the pin also.
        """

    if request.method == "POST":

        """THIS QUERY CONFIRM THAT POST IS LIKED BY CURRENT_USER OR NOT"""
        like = Like.query.filter_by(user_id=current_user.id, pin_id=pin_id).first()
        response = {}
        if like:
            db.session.delete(like)
            db.session.commit()
            response['like'] = False
        else:
            like = Like(user_id=current_user.id, pin_id=pin_id)
            db.session.add(like)
            db.session.commit()
            response['like'] = True

        """THIS QUERY FETCHED ALL LIKES COUNT OF PIN USING PIN_ID"""
        like_values = Like.query.filter_by(pin_id=pin_id).count()
        response['like_value'] = like_values

        return jsonify(response)
    else:
        return redirect(url_for('main.home_page'))


class CreateComment(View):
    """add comment to pin route
    """

    methods = ['POST']
    decorators = [login_required]

    def dispatch_request(self, pin_id=None):
        text = request.form.get('text')

        if not text:
            flash(pin_empty_comment_msg, 'info')
        else:
            pin = Pin.query.filter_by(id=pin_id)
            if pin:
                comment = Comment(text=text, user_id=current_user.id, pin_id=pin_id)
                db.session.add(comment)
                db.session.commit()
            else:
                flash(pin_not_exist_msg, 'info')
                return redirect(url_for('main.home_page'))
        return redirect(url_for('pins.selected_pin', pin_id=pin_id))


pins.add_url_rule('/pin/<int:pin_id>/comment', view_func=CreateComment.as_view('create_comment'))


class DeleteComment(View):
    """delete comment from pin route."""

    methods = ['POST', 'GET']
    decorators = [login_required]

    def dispatch_request(self, comment_id=None, pin_id=None):
        """
        :param comment_id: integer
        :param pin_id: integer
        :return: redirect to home page
        """

        comment = Comment.query.filter_by(id=comment_id).first()
        if comment is not None:
            if comment.user_id == current_user.id:
                Comment.query.filter_by(id=comment_id).delete()
                db.session.commit()
            else:
                flash(pin_comment_access_msg, 'warning')
        else:
            flash(pin_comment_not_exist_msg, 'warning')
            return redirect(url_for('main.home_page'))
        return redirect(url_for('pins.selected_pin', pin_id=pin_id))


pins.add_url_rule('/pin/<int:pin_id>/comment/<int:comment_id>/delete',
                  view_func=DeleteComment.as_view('delete_comment'))


class DownloadPin(View):
    """download pin route."""

    methods = ['GET']
    decorators = [login_required]

    def dispatch_request(self, pin_id=None):
        """generate file path and send file
        :param pin_id: integer
        :return: redirect to home page
        """

        pin = Pin.query.filter_by(id=pin_id).first()
        if pin:
            path = 'static/pin_img/' + pin.pin_pic
            return send_file(path, as_attachment=True)
        else:
            flash(pin_not_exist_msg, 'warning')
            return redirect(url_for('main.home_page'))


pins.add_url_rule('/pin/<int:pin_id>/download', view_func=DownloadPin.as_view('download_pin'))
