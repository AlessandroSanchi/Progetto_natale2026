from app.db import get_db
from datetime import datetime

def get_all_cards():
    db = get_db()
    query = """
        SELECT c.id, c.name, c.set_name, c.card_number, c.rarity, c.condition,
               c.quantity, c.price, c.image_url, c.created, c.updated, c.user_id, u.username
        FROM card c
        JOIN user u ON c.user_id = u.id
        ORDER BY c.created DESC
    """
    cards = db.execute(query).fetchall()
    result = []
    for card in cards:
        card_dict = dict(card)
        card_dict['created'] = datetime.fromisoformat(card_dict['created'])
        card_dict['updated'] = datetime.fromisoformat(card_dict['updated'])
        result.append(card_dict)
    return result

def get_user_cards(user_id):
    db = get_db()
    query = """
        SELECT c.id, c.name, c.set_name, c.card_number, c.rarity, c.condition,
               c.quantity, c.price, c.image_url, c.created, c.updated
        FROM card c
        WHERE c.user_id = ?
        ORDER BY c.created DESC
    """
    cards = db.execute(query, (user_id,)).fetchall()
    result = []
    for card in cards:
        card_dict = dict(card)
        card_dict['created'] = datetime.fromisoformat(card_dict['created'])
        card_dict['updated'] = datetime.fromisoformat(card_dict['updated'])
        result.append(card_dict)
    return result

def get_card_by_id(card_id):
    db = get_db()
    query = """
        SELECT c.id, c.name, c.set_name, c.card_number, c.rarity, c.condition,
               c.quantity, c.price, c.image_url, c.created, c.updated, c.user_id, u.username
        FROM card c
        JOIN user u ON c.user_id = u.id
        WHERE c.id = ?
    """
    card = db.execute(query, (card_id,)).fetchone()
    if card:
        card_dict = dict(card)
        card_dict['created'] = datetime.fromisoformat(card_dict['created'])
        card_dict['updated'] = datetime.fromisoformat(card_dict['updated'])
        return card_dict
    return card

def create_card(name, set_name, card_number, rarity, condition, quantity, price, image_url, user_id):
    db = get_db()
    db.execute(
        'INSERT INTO card (name, set_name, card_number, rarity, condition, quantity, price, image_url, user_id)'
        ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (name, set_name, card_number, rarity, condition, quantity, price, image_url, user_id)
    )
    db.commit()

def update_card(card_id, name, set_name, card_number, rarity, condition, quantity, price, image_url):
    db = get_db()
    db.execute(
        'UPDATE card SET name = ?, set_name = ?, card_number = ?, rarity = ?, condition = ?, quantity = ?, price = ?, image_url = ?, updated = CURRENT_TIMESTAMP'
        ' WHERE id = ?',
        (name, set_name, card_number, rarity, condition, quantity, price, image_url, card_id)
    )
    db.commit()

def delete_card(card_id):
    db = get_db()
    db.execute('DELETE FROM card WHERE id = ?', (card_id,))
    db.commit()

def get_collection_value(user_id):
    db = get_db()
    query = """
        SELECT SUM(price * quantity) as total_value
        FROM card
        WHERE user_id = ?
    """
    result = db.execute(query, (user_id,)).fetchone()
    return result['total_value'] if result['total_value'] else 0.0

def get_user_cards_by_username(username):
    db = get_db()
    query = """
        SELECT c.id, c.name, c.set_name, c.card_number, c.rarity, c.condition,
               c.quantity, c.price, c.image_url, c.created, c.updated
        FROM card c
        JOIN user u ON c.user_id = u.id
        WHERE u.username = ?
        ORDER BY c.created DESC
    """
    cards = db.execute(query, (username,)).fetchall()
    result = []
    for card in cards:
        card_dict = dict(card)
        card_dict['created'] = datetime.fromisoformat(card_dict['created'])
        card_dict['updated'] = datetime.fromisoformat(card_dict['updated'])
        result.append(card_dict)
    return result

def get_collection_value_by_username(username):
    db = get_db()
    query = """
        SELECT SUM(price * quantity) as total_value
        FROM card c
        JOIN user u ON c.user_id = u.id
        WHERE u.username = ?
    """
    result = db.execute(query, (username,)).fetchone()
    return result['total_value'] if result['total_value'] else 0.0