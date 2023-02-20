from sqlalchemy import *
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, scoped_session

engine = create_engine("postgresql://postgres:24062004@localhost:5432/article")

SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

BaseModel = declarative_base()


class User(BaseModel):
    __tablename__ = "users"

    id = Column(Integer, Identity(start=1, cycle=False), primary_key=True)
    username = Column(String, unique=true)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone = Column(String)
    user_status = Column(Integer)


class Article(BaseModel):
    __tablename__ = "article"

    id = Column(Integer, Identity(start=1, cycle=False), primary_key=True)
    name = Column(String(100))
    text = Column(String(2000))
    version = Column(Integer, default=0)
    creator_id = Column(Integer, ForeignKey('users.id'))

    articleCreator = relationship(User, foreign_keys=[creator_id], backref="id_creator", lazy="joined")


class Change(BaseModel):
    __tablename__ = "change"

    id = Column(Integer, Identity(start=1, cycle=False), primary_key=True)
    article_id = Column(Integer, ForeignKey('article.id'))
    article_version = Column(Integer)
    old_text = Column(String(2000))
    new_text = Column(String(2000))
    status = Column(String(9), default='in review')
    proposer_id = Column(Integer, ForeignKey('users.id'))

    articleChanged = relationship(Article, foreign_keys=[article_id], backref="id_article", lazy="joined")
    changeProposer = relationship(User, foreign_keys=[proposer_id], backref="id_proposer", lazy="joined")
    CheckConstraint(status.in_(['accepted', 'in review', 'denied']))


class Review(BaseModel):
    __tablename__ = "review"

    id = Column(Integer, Identity(start=1, cycle=False), primary_key=True)
    change_id = Column(Integer, ForeignKey('change.id'), unique=true)
    verdict = Column(Boolean)
    comment = Column(String(200))
    reviewer_id = Column(Integer, ForeignKey('users.id'))

    changeReviewed = relationship(Change, foreign_keys=[change_id], backref="id_change", lazy="joined")
    reviewer = relationship(User, foreign_keys=[reviewer_id], backref="id_reviewer", lazy="joined")
