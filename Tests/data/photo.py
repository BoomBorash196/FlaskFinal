from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase


class Photo(SqlAlchemyBase):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    # Добавьте параметр back_populates для связи с моделью User
    user = relationship('User', back_populates='photos')
