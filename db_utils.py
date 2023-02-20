from models import *


def create_entry(model_class, *, commit=True, **kwargs):
    session = Session()
    session.expire_on_commit = false
    entry = model_class(**kwargs)
    session.add(entry)
    if commit:
        session.commit()
    return session.query(model_class).order_by(desc(model_class.id)).first()


def get_entry_by_id(model_class, id, **kwargs):
    session = Session()
    return session.query(model_class).filter_by(id=id, **kwargs).one()


def update_entry(model_class, id, *, commit=True, **kwargs):
    session = Session()
    for key, value in kwargs.items():
        session.query(model_class).filter(model_class.id == id).update({key: value})
    if commit:
        session.commit()
    entry = session.query(model_class).filter_by(id=id, **kwargs).one()
    return entry


def delete_entry(model_class, id, commit=True, **kwargs):
    session = Session()
    entry = session.query(model_class).filter_by(id=id, **kwargs).one()
    if entry != null:
        session.query(model_class).filter_by(id=id, **kwargs).delete()
    if commit:
        session.commit()
