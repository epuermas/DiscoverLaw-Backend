from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, String
db = SQLAlchemy()


class User(db.Model):
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False, default='')
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=False, nullable=False)
    zipcode = db.Column(db.String(120), unique=False, nullable=False)
    # questions = db.relationship(Question)

    def __repr__(self): 
        return '<User %r>' % self.name

    def serialize(self):
        return {
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "zipcode": self.zipcode,
            "id": self.id
        }
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # name = db.Column(db.String(80), unique=False, nullable=False)
    question = db.Column(db.String(1000), unique=False, nullable=False)
    user = relationship(User)
    user_id = Column(Integer, ForeignKey('user.id'))


    def __repr__(self): 
        return '<Question %r>' % self.question

    def serialize(self):
        return {
            "question": self.question,
            "id": self.id
        
        }


class Lawyer(db.Model):
    __tablename__='lawyer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False, default='')
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)
    zipcode = db.Column(db.String(120), unique=False, nullable=False)
    lawfirm = db.Column(db.String(120), unique=False, nullable=False)
    phone = db.Column(db.String(120), unique=False, nullable=False)
    # answers = db.relationship(Answers)

    def __repr__(self): 
        return '<Lawyer %r>' % self.name

    def serialize(self):
        return {
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "zipcode": self.zipcode,
            "id": self.id,
            "lawfirm": self.lawfirm,
            "phone": self.phone
        }

class Answers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answers = db.Column(db.String(1000), unique=False, nullable=False)#, default='')
    # lawyer = relationship(Lawyer)
    # lawyer_id = Column(Integer, ForeignKey('lawyer.id'))

    def __repr__(self): 
        return '<Answers %r>' % self.answers

    def serialize(self):
        return {
            "answers": self.answers,
            "id": self.id
        }