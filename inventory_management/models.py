from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from inventory_management.database import Base

class Inventory(Base):
    __tablename__ = 'inventory'
    
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    stock_level = Column(Integer)
    price = Column(Float)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    
    supplier = relationship("Suppliers", back_populates="products")

class Suppliers(Base):
    __tablename__ = 'suppliers'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    contact_info = Column(String)
    
    products = relationship("Inventory", back_populates="supplier")

class Orders(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('inventory.id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    order_date = Column(String)
    quantity = Column(Integer)
    
    product = relationship("Inventory")
    supplier = relationship("Suppliers")
