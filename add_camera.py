
from app import app, db, Camera

camera = Camera(token='234')

try:
    with app.app_context():
        db.session.add(camera)
        db.session.commit()
except Exception as e:
    print('Oops', e)