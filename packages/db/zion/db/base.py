from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class DbBaseModel(DeclarativeBase, MappedAsDataclass):
    pass
