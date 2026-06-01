import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional, List

def get_db():
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    return conn


def register_business(owner_id: int, business_name: str, gst_id: str, 
                     business_type: str, phone: str, email: str, 
                     address: str, city: str, state: str, pincode: str) -> Dict[str, Any]:
    """Register a new business account"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        registration_date = datetime.now().isoformat()
        
        cur.execute("""
            INSERT INTO businesses (
                owner_id, business_name, gst_id, business_type,
                phone, email, address, city, state, pincode,
                registration_date, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            owner_id, business_name, gst_id, business_type,
            phone, email, address, city, state, pincode,
            registration_date, 'active'
        ))
        
        business_id = cur.lastrowid
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'business_id': business_id}
    except sqlite3.IntegrityError as e:
        return {'success': False, 'error': f'Business already exists: {str(e)}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_business_by_id(business_id: int) -> Optional[Dict]:
    """Get business details by ID"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM businesses WHERE id = ?", (business_id,))
        business = cur.fetchone()
        
        conn.close()
        
        return dict(business) if business else None
    except Exception as e:
        print(f"Error fetching business: {e}")
        return None


def get_user_businesses(user_id: int) -> List[Dict]:
    """Get all businesses owned by a user"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM businesses WHERE owner_id = ? ORDER BY registration_date DESC
        """, (user_id,))
        
        businesses = cur.fetchall()
        conn.close()
        
        return [dict(b) for b in businesses]
    except Exception as e:
        print(f"Error fetching businesses: {e}")
        return []


def create_branch(business_id: int, branch_name: str, address: str, 
                 city: str, state: str, pincode: str, phone: str, 
                 manager_id: Optional[int] = None) -> Dict[str, Any]:
    """Create a new branch for a business"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        registration_date = datetime.now().isoformat()
        
        cur.execute("""
            INSERT INTO branches (
                business_id, branch_name, address, city, state, pincode,
                phone, manager_id, registration_date, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            business_id, branch_name, address, city, state, pincode,
            phone, manager_id, registration_date, 'active'
        ))
        
        branch_id = cur.lastrowid
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'branch_id': branch_id}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_business_branches(business_id: int) -> List[Dict]:
    """Get all branches of a business"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM branches WHERE business_id = ? AND status = 'active'
            ORDER BY registration_date
        """, (business_id,))
        
        branches = cur.fetchall()
        conn.close()
        
        return [dict(b) for b in branches]
    except Exception as e:
        print(f"Error fetching branches: {e}")
        return []


def add_product(business_id: int, product_name: str, sku: str, 
               category: str, unit_price: float, cost_price: float,
               tax_rate: float = 0, description: str = "") -> Dict[str, Any]:
    """Add a new product to business inventory"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        registration_date = datetime.now().isoformat()
        
        cur.execute("""
            INSERT INTO products (
                business_id, product_name, sku, category, unit_price,
                cost_price, tax_rate, description, registration_date, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            business_id, product_name, sku, category, unit_price,
            cost_price, tax_rate, description, registration_date, 'active'
        ))
        
        product_id = cur.lastrowid
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'product_id': product_id}
    except sqlite3.IntegrityError:
        return {'success': False, 'error': 'SKU already exists'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_business_products(business_id: int) -> List[Dict]:
    """Get all products of a business"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM products WHERE business_id = ? AND status = 'active'
            ORDER BY product_name
        """, (business_id,))
        
        products = cur.fetchall()
        conn.close()
        
        return [dict(p) for p in products]
    except Exception as e:
        print(f"Error fetching products: {e}")
        return []


def update_stock(branch_id: int, product_id: int, new_quantity: float,
                transaction_type: str = "adjustment", reference_id: str = "",
                notes: str = "") -> Dict[str, Any]:
    """Update stock for a product in a branch"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Get or create inventory record
        cur.execute("""
            SELECT * FROM inventory WHERE branch_id = ? AND product_id = ?
        """, (branch_id, product_id))
        
        inventory = cur.fetchone()
        
        if not inventory:
            # Create new inventory record
            cur.execute("""
                INSERT INTO inventory (branch_id, product_id, stock_quantity, last_updated)
                VALUES (?, ?, ?, ?)
            """, (branch_id, product_id, new_quantity, datetime.now().isoformat()))
            inventory_id = cur.lastrowid
        else:
            inventory_id = inventory['id']
            # Update existing record
            cur.execute("""
                UPDATE inventory SET stock_quantity = ?, last_updated = ?
                WHERE id = ?
            """, (new_quantity, datetime.now().isoformat(), inventory_id))
        
        # Log transaction
        cur.execute("""
            INSERT INTO stock_transactions 
            (inventory_id, transaction_type, quantity, reference_id, notes, transaction_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (inventory_id, transaction_type, new_quantity, reference_id, notes, 
              datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'inventory_id': inventory_id}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_branch_inventory(branch_id: int) -> List[Dict]:
    """Get inventory for a branch"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT i.*, p.product_name, p.sku, p.unit_price, p.cost_price
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            WHERE i.branch_id = ?
            ORDER BY p.product_name
        """, (branch_id,))
        
        inventory = cur.fetchall()
        conn.close()
        
        return [dict(item) for item in inventory]
    except Exception as e:
        print(f"Error fetching inventory: {e}")
        return []


def get_inventory_item(branch_id: int, product_id: int) -> Optional[Dict]:
    """Get one inventory row for a branch/product pair."""
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT i.*, p.product_name, p.sku, p.unit_price, p.cost_price, p.tax_rate
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            WHERE i.branch_id = ? AND i.product_id = ?
        """, (branch_id, product_id))

        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None
    except Exception as e:
        print(f"Error fetching inventory item: {e}")
        return None


def add_supplier(business_id: int, supplier_name: str, contact_person: str,
                email: str, phone: str, address: str, city: str, state: str,
                pincode: str, gst_id: str = "", payment_terms: str = "") -> Dict[str, Any]:
    """Add a new supplier"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        registration_date = datetime.now().isoformat()
        
        cur.execute("""
            INSERT INTO suppliers (
                business_id, supplier_name, contact_person, email, phone,
                address, city, state, pincode, gst_id, payment_terms,
                registration_date, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            business_id, supplier_name, contact_person, email, phone,
            address, city, state, pincode, gst_id, payment_terms,
            registration_date, 'active'
        ))
        
        supplier_id = cur.lastrowid
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'supplier_id': supplier_id}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_business_suppliers(business_id: int) -> List[Dict]:
    """Get all suppliers of a business"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM suppliers WHERE business_id = ? AND status = 'active'
            ORDER BY supplier_name
        """, (business_id,))
        
        suppliers = cur.fetchall()
        conn.close()
        
        return [dict(s) for s in suppliers]
    except Exception as e:
        print(f"Error fetching suppliers: {e}")
        return []


def create_invoice(
    business_id: int,
    branch_id: int,
    customer_name: str,
    product_id: int,
    quantity: float,
    created_by: Optional[int] = None,
    customer_email: str = "",
    customer_phone: str = "",
    due_date: str = "",
    notes: str = "",
) -> Dict[str, Any]:
    """Create a sales invoice, reduce stock, and record output GST."""
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM products WHERE id = ? AND business_id = ?", (product_id, business_id))
        product = cur.fetchone()
        if not product:
            conn.close()
            return {"success": False, "error": "Product not found"}

        now = datetime.now().isoformat()
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        unit_price = float(product["unit_price"] or 0)
        tax_rate = float(product["tax_rate"] or 0)
        subtotal = round(quantity * unit_price, 2)
        tax_amount = round(subtotal * tax_rate / 100, 2)
        total_amount = round(subtotal + tax_amount, 2)

        cur.execute("""
            INSERT INTO invoices (
                business_id, branch_id, invoice_number, customer_name,
                customer_email, customer_phone, invoice_date, due_date,
                subtotal, tax_amount, total_amount, payment_status, notes,
                created_by, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            business_id, branch_id, invoice_number, customer_name,
            customer_email, customer_phone, datetime.now().date().isoformat(), due_date,
            subtotal, tax_amount, total_amount, "unpaid", notes,
            created_by, now
        ))

        invoice_id = cur.lastrowid
        cur.execute("""
            INSERT INTO invoice_items (
                invoice_id, product_id, description, quantity, unit_price, tax_rate, line_total
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            invoice_id, product_id, product["product_name"], quantity,
            unit_price, tax_rate, total_amount
        ))

        cur.execute("""
            SELECT * FROM inventory WHERE branch_id = ? AND product_id = ?
        """, (branch_id, product_id))
        inventory = cur.fetchone()
        if inventory:
            new_quantity = float(inventory["stock_quantity"] or 0) - quantity
            inventory_id = inventory["id"]
            cur.execute("""
                UPDATE inventory SET stock_quantity = ?, last_updated = ? WHERE id = ?
            """, (new_quantity, now, inventory_id))
        else:
            new_quantity = -quantity
            cur.execute("""
                INSERT INTO inventory (branch_id, product_id, stock_quantity, last_updated)
                VALUES (?, ?, ?, ?)
            """, (branch_id, product_id, new_quantity, now))
            inventory_id = cur.lastrowid

        cur.execute("""
            INSERT INTO stock_transactions (
                inventory_id, transaction_type, quantity, reference_id, notes, transaction_date
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            inventory_id, "sale", -quantity, invoice_number,
            f"Invoice sale to {customer_name}", now
        ))

        half_rate = tax_rate / 2
        half_tax = round(tax_amount / 2, 2)
        cur.execute("""
            INSERT INTO gst_transactions (
                business_id, transaction_type, invoice_id, taxable_amount,
                cgst_rate, cgst_amount, sgst_rate, sgst_amount,
                igst_rate, igst_amount, total_tax, transaction_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            business_id, "sales", invoice_id, subtotal,
            half_rate, half_tax, half_rate, tax_amount - half_tax,
            0, 0, tax_amount, datetime.now().date().isoformat()
        ))

        conn.commit()
        conn.close()

        return {"success": True, "invoice_id": invoice_id, "invoice_number": invoice_number}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_business_invoices(business_id: int) -> List[Dict]:
    """Get invoices with branch names."""
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT i.*, b.branch_name
            FROM invoices i
            JOIN branches b ON i.branch_id = b.id
            WHERE i.business_id = ?
            ORDER BY i.created_at DESC
        """, (business_id,))

        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching invoices: {e}")
        return []


def mark_invoice_paid(invoice_id: int, business_id: int) -> Dict[str, Any]:
    """Mark an invoice as paid."""
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            UPDATE invoices
            SET payment_status = 'paid', payment_date = ?
            WHERE id = ? AND business_id = ?
        """, (datetime.now().date().isoformat(), invoice_id, business_id))

        conn.commit()
        updated = cur.rowcount
        conn.close()

        if not updated:
            return {"success": False, "error": "Invoice not found"}
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_purchase_order(
    business_id: int,
    supplier_id: int,
    branch_id: int,
    product_id: int,
    quantity: float,
    unit_price: float,
    created_by: Optional[int] = None,
    expected_delivery_date: str = "",
    notes: str = "",
) -> Dict[str, Any]:
    """Create a received purchase order, add stock, and record input GST."""
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM products WHERE id = ? AND business_id = ?", (product_id, business_id))
        product = cur.fetchone()
        if not product:
            conn.close()
            return {"success": False, "error": "Product not found"}

        now = datetime.now().isoformat()
        po_number = f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        tax_rate = float(product["tax_rate"] or 0)
        subtotal = round(quantity * unit_price, 2)
        tax_amount = round(subtotal * tax_rate / 100, 2)
        total_amount = round(subtotal + tax_amount, 2)

        cur.execute("""
            INSERT INTO purchase_orders (
                business_id, supplier_id, po_number, order_date,
                expected_delivery_date, subtotal, tax_amount, total_amount,
                status, delivery_date, notes, created_by, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            business_id, supplier_id, po_number, datetime.now().date().isoformat(),
            expected_delivery_date, subtotal, tax_amount, total_amount,
            "received", datetime.now().date().isoformat(), notes, created_by, now
        ))

        po_id = cur.lastrowid
        cur.execute("""
            INSERT INTO po_items (
                po_id, product_id, description, quantity, unit_price, tax_rate, line_total
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            po_id, product_id, product["product_name"], quantity,
            unit_price, tax_rate, total_amount
        ))

        cur.execute("""
            SELECT * FROM inventory WHERE branch_id = ? AND product_id = ?
        """, (branch_id, product_id))
        inventory = cur.fetchone()
        if inventory:
            new_quantity = float(inventory["stock_quantity"] or 0) + quantity
            inventory_id = inventory["id"]
            cur.execute("""
                UPDATE inventory SET stock_quantity = ?, last_updated = ? WHERE id = ?
            """, (new_quantity, now, inventory_id))
        else:
            cur.execute("""
                INSERT INTO inventory (branch_id, product_id, stock_quantity, last_updated)
                VALUES (?, ?, ?, ?)
            """, (branch_id, product_id, quantity, now))
            inventory_id = cur.lastrowid

        cur.execute("""
            INSERT INTO stock_transactions (
                inventory_id, transaction_type, quantity, reference_id, notes, transaction_date
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            inventory_id, "purchase", quantity, po_number,
            "Purchase order received", now
        ))

        half_rate = tax_rate / 2
        half_tax = round(tax_amount / 2, 2)
        cur.execute("""
            INSERT INTO gst_transactions (
                business_id, transaction_type, po_id, taxable_amount,
                cgst_rate, cgst_amount, sgst_rate, sgst_amount,
                igst_rate, igst_amount, total_tax, transaction_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            business_id, "purchase", po_id, subtotal,
            half_rate, half_tax, half_rate, tax_amount - half_tax,
            0, 0, tax_amount, datetime.now().date().isoformat()
        ))

        conn.commit()
        conn.close()
        return {"success": True, "po_id": po_id, "po_number": po_number}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_business_purchase_orders(business_id: int) -> List[Dict]:
    """Get purchase orders with supplier names."""
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT po.*, s.supplier_name
            FROM purchase_orders po
            JOIN suppliers s ON po.supplier_id = s.id
            WHERE po.business_id = ?
            ORDER BY po.created_at DESC
        """, (business_id,))

        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching purchase orders: {e}")
        return []


def get_gst_report(business_id: int) -> Dict[str, Any]:
    """Summarize output GST, input GST, and net payable."""
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM gst_transactions
            WHERE business_id = ?
            ORDER BY transaction_date DESC, id DESC
        """, (business_id,))
        rows = [dict(row) for row in cur.fetchall()]
        conn.close()

        output_tax = sum(float(row["total_tax"] or 0) for row in rows if row["transaction_type"] == "sales")
        input_tax = sum(float(row["total_tax"] or 0) for row in rows if row["transaction_type"] == "purchase")

        return {
            "output_tax": round(output_tax, 2),
            "input_tax": round(input_tax, 2),
            "net_payable": round(output_tax - input_tax, 2),
            "transactions": rows,
        }
    except Exception as e:
        print(f"Error fetching GST report: {e}")
        return {"output_tax": 0, "input_tax": 0, "net_payable": 0, "transactions": []}


def get_business_stats(business_id: int) -> Dict[str, Any]:
    """Get business statistics"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Total revenue
        cur.execute("""
            SELECT COALESCE(SUM(total_amount), 0) as total_revenue
            FROM invoices WHERE business_id = ? AND payment_status = 'paid'
        """, (business_id,))
        row = cur.fetchone()
        revenue = row['total_revenue'] if row else 0
        
        # Total pending payments
        cur.execute("""
            SELECT COALESCE(SUM(total_amount), 0) as pending_amount
            FROM invoices WHERE business_id = ? AND payment_status = 'unpaid'
        """, (business_id,))
        row = cur.fetchone()
        pending = row['pending_amount'] if row else 0
        
        # Total products
        cur.execute("""
            SELECT COUNT(*) as product_count
            FROM products WHERE business_id = ? AND status = 'active'
        """, (business_id,))
        row = cur.fetchone()
        products = row['product_count'] if row else 0
        
        # Total branches
        cur.execute("""
            SELECT COUNT(*) as branch_count
            FROM branches WHERE business_id = ? AND status = 'active'
        """, (business_id,))
        row = cur.fetchone()
        branches = row['branch_count'] if row else 0

        cur.execute("""
            SELECT COALESCE(SUM(total_amount), 0) as purchase_total
            FROM purchase_orders WHERE business_id = ?
        """, (business_id,))
        row = cur.fetchone()
        purchases = row['purchase_total'] if row else 0

        cur.execute("""
            SELECT COUNT(*) as low_stock_count
            FROM inventory i
            JOIN branches b ON i.branch_id = b.id
            WHERE b.business_id = ? AND i.stock_quantity < i.reorder_level
        """, (business_id,))
        row = cur.fetchone()
        low_stock = row['low_stock_count'] if row else 0

        gst = get_gst_report(business_id)
        
        conn.close()
        
        return {
            'total_revenue': revenue,
            'pending_amount': pending,
            'total_products': products,
            'total_branches': branches,
            'purchase_total': purchases,
            'low_stock_count': low_stock,
            'gst_payable': gst.get('net_payable', 0)
        }
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {}
