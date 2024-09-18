import click
from sqlalchemy.orm import Session
from inventory_management.database import SessionLocal
from inventory_management import models

# Create a session to interact with the database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@click.group()
def cli():
    """Inventory Management System"""
    pass

### PRODUCT COMMANDS ###
@cli.group()
def product():
    """Commands related to products"""
    pass

@product.command("add")
@click.argument('name')
@click.argument('stock_level')
@click.argument('price')
@click.argument('supplier_name')
def add_product(name, stock_level, price, supplier_name):
    """Add a new product"""
    db = next(get_db())
    
    # Look up the supplier by name
    supplier = db.query(models.Suppliers).filter_by(name=supplier_name).first()
    if not supplier:
        click.echo(f"Supplier '{supplier_name}' not found.")
        return
    
    new_product = models.Inventory(
        product_name=name,
        stock_level=stock_level,
        price=price,
        supplier_id=supplier.id
    )
    db.add(new_product)
    db.commit()
    click.echo(f"Product '{name}' added to inventory.")

@product.command("list")
def list_products():
    """List all products"""
    db = next(get_db())
    products = db.query(models.Inventory).all()
    if products:
        for product in products:
            click.echo(f"ID: {product.id}, Name: {product.product_name}, Stock: {product.stock_level}, Price: {product.price}, Supplier: {product.supplier.name}")
    else:
        click.echo("No products found in the inventory.")

@product.command("update-stock")
@click.argument('product_name')
@click.argument('new_stock')
def update_stock(product_name, new_stock):
    """Update the stock level of a product"""
    db = next(get_db())
    product = db.query(models.Inventory).filter_by(product_name=product_name).first()
    if product:
        product.stock_level = new_stock
        db.commit()
        click.echo(f"Stock for '{product_name}' updated to {new_stock}.")
    else:
        click.echo(f"Product '{product_name}' not found.")

@product.command("remove")
@click.argument('product_name')
def remove_product(product_name):
    """Remove a product from the inventory"""
    db = next(get_db())
    product = db.query(models.Inventory).filter_by(product_name=product_name).first()
    if product:
        db.delete(product)
        db.commit()
        click.echo(f"Product '{product_name}' removed from inventory.")
    else:
        click.echo(f"Product '{product_name}' not found.")

@product.command("low-stock")
@click.argument('threshold')
def low_stock(threshold):
    """List products below a stock threshold"""
    db = next(get_db())
    products = db.query(models.Inventory).filter(models.Inventory.stock_level < threshold).all()
    if products:
        for product in products:
            click.echo(f"Product: {product.product_name}, Stock: {product.stock_level}")
    else:
        click.echo(f"No products below stock threshold of {threshold}.")

### SUPPLIER COMMANDS ###
@cli.group()
def supplier():
    """Commands related to suppliers"""
    pass

@supplier.command("add")
@click.argument('name')
@click.argument('contact_info')
def add_supplier(name, contact_info):
    """Add a new supplier"""
    db = next(get_db())
    new_supplier = models.Suppliers(name=name, contact_info=contact_info)
    db.add(new_supplier)
    db.commit()
    click.echo(f"Supplier '{name}' added.")

@supplier.command("list")
def list_suppliers():
    """List all suppliers"""
    db = next(get_db())
    suppliers = db.query(models.Suppliers).all()
    if suppliers:
        for supplier in suppliers:
            click.echo(f"ID: {supplier.id}, Name: {supplier.name}, Contact Info: {supplier.contact_info}")
    else:
        click.echo("No suppliers found.")

@supplier.command("update-contact")
@click.argument('supplier_name')
@click.argument('new_contact_info')
def update_supplier(supplier_name, new_contact_info):
    """Update supplier contact info"""
    db = next(get_db())
    supplier = db.query(models.Suppliers).filter_by(name=supplier_name).first()
    if supplier:
        supplier.contact_info = new_contact_info
        db.commit()
        click.echo(f"Contact info for '{supplier_name}' updated.")
    else:
        click.echo(f"Supplier '{supplier_name}' not found.")

@supplier.command("remove")
@click.argument('supplier_name')
def remove_supplier(supplier_name):
    """Remove a supplier"""
    db = next(get_db())
    supplier = db.query(models.Suppliers).filter_by(name=supplier_name).first()
    if supplier:
        db.delete(supplier)
        db.commit()
        click.echo(f"Supplier '{supplier_name}' removed.")
    else:
        click.echo(f"Supplier '{supplier_name}' not found.")

### ORDER COMMANDS ###
@cli.group()
def order():
    """Commands related to orders"""
    pass

@order.command("place")
@click.argument('product_name')
@click.argument('supplier_name')
@click.argument('quantity')
@click.argument('order_date')
def place_order(product_name, supplier_name, quantity, order_date):
    """Place an order to restock inventory"""
    db = next(get_db())
    
    product = db.query(models.Inventory).filter_by(product_name=product_name).first()
    supplier = db.query(models.Suppliers).filter_by(name=supplier_name).first()
    
    if not product:
        click.echo(f"Product '{product_name}' not found.")
        return
    if not supplier:
        click.echo(f"Supplier '{supplier_name}' not found.")
        return

    new_order = models.Orders(
        product_id=product.id,
        supplier_id=supplier.id,
        quantity=quantity,
        order_date=order_date
    )
    db.add(new_order)
    product.stock_level += int(quantity)  # Increase the stock
    db.commit()
    
    click.echo(f"Order placed for {quantity} units of '{product_name}' from '{supplier_name}' on {order_date}.")

@order.command("list")
def list_orders():
    """List all orders"""
    db = next(get_db())
    orders = db.query(models.Orders).all()
    if orders:
        for order in orders:
            click.echo(f"Order ID: {order.id}, Product: {order.product.product_name}, Supplier: {order.supplier.name}, Quantity: {order.quantity}, Date: {order.order_date}")
    else:
        click.echo("No orders found.")

if __name__ == "__main__":
    cli()
