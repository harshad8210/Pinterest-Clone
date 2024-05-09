from flask import Blueprint, render_template
from pinterest.models import Pin, UserInterest, PinTags
from flask.views import View
from pinterest.main.form import SearchForm
from pinterest.main.utils import user_interest_tags, user_interest_pins
from flask_login import current_user

main = Blueprint('main', __name__)


class HomePage(View):
    """home page for authentication user
    """

    def dispatch_request(self):
        pins = Pin.query.all()
        if current_user.is_authenticated:
            interested_tags = UserInterest.query.with_entities(UserInterest.tag_id).filter_by(
                user_id=current_user.id).all()
            user_interest_list = user_interest_tags(interested_tags)
            inst_pin_id = PinTags.query.filter(PinTags.tag_id.in_(user_interest_list)).all()
            user_interest_pin = user_interest_pins(inst_pin_id)
            pins = Pin.query.filter(Pin.id.in_(user_interest_pin), Pin.privacy == 0).all()

        return render_template('home.html', pins=pins)


main.add_url_rule('/', view_func=HomePage.as_view('home_page'))


@main.context_processor
def base():
    """for passing the form to the base template
    :return:
    """

    form = SearchForm()
    return dict(form=form)


@main.route('/search', methods=['POST'])
def search():
    """search for pins
    :return: searched pin page
    """

    form = SearchForm()
    pins = Pin.query.all()
    if form.validate_on_submit():
        searched_pin = form.searched.data
        selected_pins = Pin.query.filter(Pin.title.ilike('%' + searched_pin + '%')).all()
        return render_template('search.html', form=form, selected_pins=selected_pins)
    return render_template('home.html', pins=pins)
