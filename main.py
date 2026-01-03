from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from app.repositories import card_repository

bp = Blueprint('main', __name__)

@bp.app_template_filter('abbreviate')
def abbreviate_number(value):
    try:
        num = float(value)
        if num >= 1_000_000_000_000:  # Trilioni
            return f"{num / 1_000_000_000_000:.1f}t"
        elif num >= 1_000_000_000:  # Miliardi
            return f"{num / 1_000_000_000:.1f}b"
        elif num >= 1_000_000:  # Milioni
            return f"{num / 1_000_000:.1f}m"
        elif num >= 1_000:  # Migliaia
            return f"{num / 1_000:.1f}k"
        else:
            return f"{num:.2f}"
    except (ValueError, TypeError):
        return value

@bp.route('/')
def index():
    if g.user:
        cards = card_repository.get_user_cards(g.user['id'])
        total_value = card_repository.get_collection_value(g.user['id'])
    else:
        cards = []
        total_value = 0.0

    return render_template('index.html', cards=cards, total_value=total_value)

@bp.route('/about')
def about():
    return render_template('about.html')

@bp.route('/search-users', methods=('GET', 'POST'))
def search_users():
    if request.method == 'POST':
        username = request.form['username']
        return redirect(url_for('main.user_collection', username=username))
    return render_template('search_users.html')

@bp.route('/user/<username>')
def user_collection(username):
    cards = card_repository.get_user_cards_by_username(username)
    total_value = card_repository.get_collection_value_by_username(username)
    if not cards and total_value == 0.0:
        flash(f"Nessuna collezione trovata per l'utente {username}.")
        return redirect(url_for('main.search_users'))
    return render_template('user_collection.html', cards=cards, total_value=total_value, username=username)

# --- ADD CARD ---
@bp.route('/add-card', methods=('GET', 'POST'))
def add_card():
    if g.user is None:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        name = request.form['name']
        set_name = request.form['set_name']
        card_number = request.form['card_number']
        rarity = request.form.get('rarity', '')
        condition = request.form.get('condition', 'Near Mint')
        quantity_str = request.form.get('quantity', '1')
        price_str = request.form.get('price', '0.0')
        image_url = request.form.get('image_url', '')

        error = None

        if not name:
            error = 'Il nome della carta è obbligatorio.'

        if not set_name:
            error = 'Il nome del set è obbligatorio.'

        try:
            quantity = int(quantity_str)
            if quantity < 1:
                error = 'La quantità deve essere almeno 1.'
        except ValueError:
            error = 'La quantità deve essere un numero intero valido.'

        try:
            price = float(price_str)
            if price < 0:
                error = 'Il prezzo non può essere negativo.'
        except ValueError:
            error = 'Il prezzo deve essere un numero valido.'

        if error is not None:
            flash(error)
        else:
            card_repository.create_card(name, set_name, card_number, rarity, condition, quantity, price, image_url, g.user['id'])
            return redirect(url_for('main.index'))

    return render_template('card/add_card.html')

def get_card(id, check_owner=True):
    card = card_repository.get_card_by_id(id)

    if card is None:
        abort(404, f"La carta id {id} non esiste.")

    if check_owner and card['user_id'] != g.user['id']:
        abort(403)

    return card

@bp.route('/card/<int:id>/update', methods=('GET', 'POST'))
def update_card(id):
    if g.user is None:
        return redirect(url_for('auth.login'))

    card = get_card(id)

    if request.method == 'POST':
        name = request.form['name']
        set_name = request.form['set_name']
        card_number = request.form['card_number']
        rarity = request.form.get('rarity', '')
        condition = request.form.get('condition', 'Near Mint')
        quantity_str = request.form.get('quantity', '1')
        price_str = request.form.get('price', '0.0')
        image_url = request.form.get('image_url', '')

        error = None

        if not name:
            error = 'Il nome della carta è obbligatorio.'

        if not set_name:
            error = 'Il nome del set è obbligatorio.'

        try:
            quantity = int(quantity_str)
            if quantity < 1:
                error = 'La quantità deve essere almeno 1.'
        except ValueError:
            error = 'La quantità deve essere un numero intero valido.'

        try:
            price = float(price_str)
            if price < 0:
                error = 'Il prezzo non può essere negativo.'
        except ValueError:
            error = 'Il prezzo deve essere un numero valido.'

        if error is not None:
            flash(error)
        else:
            card_repository.update_card(id, name, set_name, card_number, rarity, condition, quantity, price, image_url)
            return redirect(url_for('main.index'))

    return render_template('card/update_card.html', card=card)

@bp.route('/card/<int:id>/delete', methods=('POST',))
def delete_card(id):
    if g.user is None:
        return redirect(url_for('auth.login'))

    get_card(id)

    card_repository.delete_card(id)
    return redirect(url_for('main.index'))