from sqlalchemy import Column, Integer, String, DateTime
from .base import Base
import datetime


class Brand(Base):
    """ Brand """

    __tablename__ = "brand"

    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, nullable=True)
    brand_name = Column(String(250), nullable=False)
    location = Column(String(250), nullable=False)
    email_address = Column(String(250), nullable=False)
    phone_number = Column(String(250), nullable=False)
    description = Column(String(250), nullable=True)
    last_update = Column(String(250), nullable=False)
    created_date = Column(DateTime, nullable=False)

    def __init__(self, brand_id, brand_name, description, email_address, phone_number, location, last_update):
        """ Initializes a brand """
        self.brand_id = brand_id
        self.brand_name = brand_name
        self.location = location
        self.email_address = email_address
        self.phone_number = phone_number
        self.description = description
        self.last_update = last_update
        self.created_date = datetime.datetime.now()

    def to_dict(self):
        """ Dictionary Representation for a brand """
        dict = {}
        dict['id'] = self.id
        dict['brand_id'] = self.brand_id
        dict['brand_name'] = self.brand_name
        dict['location'] = self.location
        dict['email_address'] = self.email_address
        dict['phone_number'] = self.phone_number
        dict['description'] = self.description
        dict['last_update'] = self.last_update
        dict['created_date'] = self.created_date

        return dict
