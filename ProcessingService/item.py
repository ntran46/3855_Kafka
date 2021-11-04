from sqlalchemy import Column, Integer, String, DateTime
from .base import Base
import datetime


class Item(Base):
    """ Item class """

    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, nullable=False)
    brand = Column(String(250), nullable=False)
    item_name = Column(String(250), nullable=False)
    description = Column(String(250), nullable=False)
    price = Column(String(100), nullable=False)
    quantities = Column(Integer, nullable=False)
    last_update = Column(String(250), nullable=False)
    created_date = Column(DateTime, nullable=False)

    def __init__(self, item_id, brand, item_name, description, price, quantities, last_update):
        """ Initializes a brand """
        self.item_id = item_id
        self.brand = brand
        self.item_name = item_name
        self.description = description
        self.price = price
        self.quantities = quantities
        self.last_update = last_update
        self.created_date = datetime.datetime.now()

    def to_dict(self):
        """ Dictionary Representation for a brand """
        dict = {}
        dict['id'] = self.id
        dict['item_id'] = self.item_id
        dict['brand'] = self.brand
        dict['item_name'] = self.item_name
        dict['description'] = self.description
        dict['price'] = self.price
        dict['quantities'] = self.quantities
        dict['last_update'] = self.last_update
        dict['created_date'] = self.created_date

        return dict
