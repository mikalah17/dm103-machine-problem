"""
Simple Business Process Management System
Business Process: Online Food Ordering
"""

import os
from datetime import datetime
from decimal import Decimal
from io import BytesIO

import mysql.connector
from flask import (Flask, abort, flash, g, redirect, render_template,
                   request, send_file, session, url_for)
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "bpm-food-ordering-demo")

# ------------------------------------------------------------- configuration
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "put__db_password_here"),  # <-- change this
    "database": os.environ.get("DB_NAME", "food_ordering_bpm"),
    "charset": "utf8mb4",
}

PESO = "\u20b1"
PAYMENT_METHODS = ["Cash", "GCash", "Maya", "Card"]

# PDF fonts: built-in PDF fonts can't draw the peso sign, so use Arial from
# Windows and fall back to "PHP " if it isn't found.
FONT, FONT_BOLD, CUR = "Helvetica", "Helvetica-Bold", "PHP "
try:
    pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"))
    FONT, FONT_BOLD, CUR = "Arial", "Arial-Bold", PESO
except Exception:
    pass

# order statuses
PENDING = "PENDING PAYMENT"
CONFIRMED = "CONFIRMED"
PREPARING = "PREPARING"
READY = "READY"
COMPLETED = "COMPLETED"
ALL_STATUSES = [PENDING, CONFIRMED, PREPARING, READY, COMPLETED]

# steps in the process, for display on the order page
STEPS = [
    "Order Placed",
    "Total Calculated",
    "Payment Check",
    "Order Confirmed",
    "Preparing",
    "Order Ready",
    "Completed",
]
STEP_INDEX = {PENDING: 2, CONFIRMED: 3, PREPARING: 4, READY: 5, COMPLETED: 6}

# status -> (next status, button label)
NEXT_STEP = {
    CONFIRMED: (PREPARING, "Start Preparing"),
    PREPARING: (READY, "Mark Ready"),
    READY: (COMPLETED, "Complete Order"),
}


# ----------------------------------------------------------------- database
def get_db():
    if "db" not in g:
        g.db = mysql.connector.connect(**DB_CONFIG)
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query(sql, params=(), one=False):
    cur = get_db().cursor(dictionary=True)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    if one:
        return rows[0] if rows else None
    return rows


def log_status(cur, order_id, status, remarks=None):
    cur.execute(
        "INSERT INTO order_status_log (order_id, status, remarks) VALUES (%s, %s, %s)",
        (order_id, status, remarks),
    )


@app.errorhandler(mysql.connector.Error)
def database_error(err):
    return render_template("error.html", message=str(err)), 500


# ------------------------------------------------------------ template tools
@app.template_filter("peso")
def peso(value):
    return f"{PESO}{Decimal(value):,.2f}"


@app.template_filter("order_no")
def order_no(value):
    return f"{int(value):03d}"


@app.template_filter("slug")
def slug(value):
    return value.lower().replace(" ", "-")


@app.template_filter("when")
def when(value):
    return value.strftime("%b %d, %Y %I:%M %p") if value else ""


# --------------------------------------------------------------- cart (draft)
def get_menu():
    return query(
        "SELECT id, name, price, category FROM menu_items "
        "WHERE is_available = 1 ORDER BY sort_order, id"
    )


def group_menu(menu):
    groups = {}
    for item in menu:
        groups.setdefault(item["category"], []).append(item)
    return groups


def build_cart(menu):
    """Step 3: Calculate Total Amount."""
    by_id = {m["id"]: m for m in menu}
    lines, total = [], Decimal("0")
    for entry in session.get("cart", []):
        item = by_id.get(entry["id"])
        if not item:
            continue
        subtotal = item["price"] * entry["qty"]
        total += subtotal
        lines.append({
            "id": item["id"],
            "name": item["name"],
            "price": item["price"],
            "qty": entry["qty"],
            "note": entry["note"],
            "subtotal": subtotal,
        })
    return lines, total


def sync_cart_from_form():
    """Save whatever is typed on the page (name, quantities, notes, payment)."""
    session["customer"] = request.form.get("customer", "").strip()[:100]
    method = request.form.get("payment_method")
    if method in PAYMENT_METHODS:
        session["payment_method"] = method

    cart = session.get("cart", [])
    for entry in cart:
        raw = request.form.get(f"qty_{entry['id']}")
        if raw is not None and raw.strip().isdigit():
            entry["qty"] = min(int(raw), 99)
        note = request.form.get(f"note_{entry['id']}")
        if note is not None:
            entry["note"] = note.strip()[:200]
    session["cart"] = [e for e in cart if e["qty"] > 0]
    session.modified = True


# ------------------------------------------------------------ order screen
@app.get("/")
def pos():
    menu = get_menu()
    lines, total = build_cart(menu)
    return render_template(
        "pos.html",
        menu=group_menu(menu),
        lines=lines,
        total=total,
        in_cart={line["id"]: line["qty"] for line in lines},
        customer=session.get("customer", ""),
        payment_method=session.get("payment_method", PAYMENT_METHODS[0]),
        payment_methods=PAYMENT_METHODS,
    )


@app.post("/pos")
def pos_action():
    """Every button on the order screen posts here."""
    menu = get_menu()
    available = {m["id"] for m in menu}
    sync_cart_from_form()

    cart = session.get("cart", [])
    kind, _, arg = request.form.get("action", "update").partition(":")
    item_id = int(arg) if arg.isdigit() else None
    line = next((e for e in cart if e["id"] == item_id), None)

    if kind == "add" and item_id in available:  # Step 2: Enter Food Order
        if line:
            line["qty"] = min(line["qty"] + 1, 99)
        else:
            cart.append({"id": item_id, "qty": 1, "note": ""})
    elif kind == "inc" and line:
        line["qty"] = min(line["qty"] + 1, 99)
    elif kind == "dec" and line:
        line["qty"] -= 1
    elif kind == "remove" and line:
        line["qty"] = 0
    elif kind == "clear":
        cart = []
        session["customer"] = ""
    elif kind in ("log_paid", "log_pending"):
        session["cart"] = [e for e in cart if e["qty"] > 0]
        session.modified = True
        return log_order(menu, paid=(kind == "log_paid"))

    session["cart"] = [e for e in cart if e["qty"] > 0]
    session.modified = True
    return redirect(url_for("pos"))


def log_order(menu, paid):
    """Steps 1 + 4: place the order in the database and check payment."""
    customer = session.get("customer", "")
    method = session.get("payment_method")
    lines, total = build_cart(menu)

    if not customer:
        flash("Please enter the customer's name first.", "error")
    elif not lines:
        flash("The order is empty. Tap a menu item to add it.", "error")
    elif paid and method not in PAYMENT_METHODS:
        flash("Please choose a payment method.", "error")
    else:
        order_id = save_order(customer, lines, total, method if paid else None, paid)
        session.pop("cart", None)
        session.pop("customer", None)
        if paid:
            flash(f"Order {order_id:03d} logged and paid via {method}.", "success")
        else:
            flash(f"Order {order_id:03d} logged as pending payment.", "warn")
        return redirect(url_for("view_order", order_id=order_id))
    return redirect(url_for("pos"))


def save_order(customer, lines, total, method, paid):
    db = get_db()
    cur = db.cursor()
    try:
        status = CONFIRMED if paid else PENDING  # Paid? YES -> Confirmed, NO -> Pending
        cur.execute(
            "INSERT INTO orders (customer_name, total_amount, payment_method, "
            "payment_status, status, paid_at) VALUES (%s, %s, %s, %s, %s, %s)",
            (customer, total, method, "PAID" if paid else "UNPAID", status,
             datetime.now() if paid else None),
        )
        order_id = cur.lastrowid
        cur.executemany(
            "INSERT INTO order_items (order_id, menu_item_id, item_name, unit_price, "
            "quantity, note) VALUES (%s, %s, %s, %s, %s, %s)",
            [(order_id, l["id"], l["name"], l["price"], l["qty"], l["note"] or None)
             for l in lines],
        )
        log_status(cur, order_id, "ORDER PLACED",
                   f"{sum(l['qty'] for l in lines)} item(s), total {total:,.2f}")
        if paid:
            log_status(cur, order_id, CONFIRMED, f"Paid via {method}")
        else:
            log_status(cur, order_id, PENDING, "Waiting for payment")
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        cur.close()
    return order_id


# ------------------------------------------------------------ orders & process
def get_order_or_404(order_id):
    order = query("SELECT * FROM orders WHERE id = %s", (order_id,), one=True)
    if not order:
        abort(404)
    return order


@app.get("/orders")
def all_orders():
    selected = request.args.get("status", "")
    sql = (
        "SELECT o.*, GROUP_CONCAT(CONCAT(i.item_name, ' x', i.quantity) "
        "ORDER BY i.id SEPARATOR ', ') AS food "
        "FROM orders o LEFT JOIN order_items i ON i.order_id = o.id "
    )
    params = ()
    if selected in ALL_STATUSES:
        sql += "WHERE o.status = %s "
        params = (selected,)
    sql += "GROUP BY o.id ORDER BY o.id DESC"

    counts = {r["status"]: r["n"] for r in
              query("SELECT status, COUNT(*) AS n FROM orders GROUP BY status")}
    return render_template(
        "orders.html",
        orders=query(sql, params),
        statuses=ALL_STATUSES,
        counts=counts,
        total_count=sum(counts.values()),
        selected=selected if selected in ALL_STATUSES else "",
        next_step=NEXT_STEP,
    )


@app.get("/order/<int:order_id>")
def view_order(order_id):
    order = get_order_or_404(order_id)
    items = query("SELECT * FROM order_items WHERE order_id = %s ORDER BY id",
                  (order_id,))
    history = query("SELECT * FROM order_status_log WHERE order_id = %s ORDER BY id",
                    (order_id,))
    return render_template(
        "order.html",
        order=order,
        items=items,
        food=", ".join(f"{i['item_name']} x{i['quantity']}" for i in items),
        history=history,
        steps=STEPS,
        current=STEP_INDEX[order["status"]],
        next_step=NEXT_STEP.get(order["status"]),
        payment_methods=PAYMENT_METHODS,
        PENDING=PENDING,
        COMPLETED=COMPLETED,
    )


@app.get("/order/<int:order_id>/receipt.pdf")
def receipt_pdf(order_id):
    """Download the receipt as an 80mm thermal-style PDF."""
    order = get_order_or_404(order_id)
    items = query("SELECT * FROM order_items WHERE order_id = %s ORDER BY id",
                  (order_id,))

    W, M, LH, SIZE = 80 * mm, 5 * mm, 12, 9
    inner = W - 2 * M
    money = lambda v: f"{CUR}{Decimal(v):,.2f}"

    # rows: (kind, left, right, bold)
    rows = []

    def add(left="", right="", bold=False, kind="text"):
        rows.append((kind, left, right, bold))

    def wrapped(text, width, bold=False):
        return simpleSplit(text, FONT_BOLD if bold else FONT, SIZE, width)

    add("FOOD ORDERING", bold=True, kind="center")
    add("Order Receipt", kind="center")
    add(kind="line")
    add("Order No.", f"{order['id']:03d}")
    add("Customer", order["customer_name"])
    if order.get("created_at"):
        add("Date", order["created_at"].strftime("%b %d, %Y %I:%M %p"))
    add(kind="line")

    for i in items:
        sub = i["unit_price"] * i["quantity"]
        parts = wrapped(f"{i['quantity']} x {i['item_name']}", inner - 22 * mm)
        add(parts[0], money(sub))
        for extra in parts[1:]:
            add(extra)
        add(f"@ {money(i['unit_price'])} each")
        if i.get("note"):
            for n in wrapped(f"Note: {i['note']}", inner):
                add(n)

    add(kind="line")
    add("TOTAL", money(order["total_amount"]), bold=True)
    add(kind="line")
    pay = order["payment_status"] + (
        f" ({order['payment_method']})" if order["payment_method"] else "")
    add("Payment", pay)
    if order.get("paid_at"):
        add("Paid on", order["paid_at"].strftime("%b %d, %Y %I:%M %p"))
    add("Order Status", order["status"])
    add(kind="line")
    add("Thank you for your order!", kind="center")

    H = 2 * M + len(rows) * LH
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(W, H))
    y = H - M - SIZE

    for kind, left, right, bold in rows:
        c.setFont(FONT_BOLD if bold else FONT, SIZE)
        if kind == "line":
            c.setDash(2, 2)
            c.line(M, y + SIZE / 2 - 1, W - M, y + SIZE / 2 - 1)
            c.setDash()
        elif kind == "center":
            c.drawCentredString(W / 2, y, left)
        elif kind == "text":
            c.drawString(M, y, left)
            if right:
                c.drawRightString(W - M, y, right)
        y -= LH

    c.showPage()
    c.save()
    buf.seek(0)
    return send_file(buf, mimetype="application/pdf", as_attachment=True,
                     download_name=f"receipt-{order['id']:03d}.pdf")


@app.post("/order/<int:order_id>/pay")
def pay_order(order_id):
    """Pending Payment -> paid -> Order Confirmed."""
    order = get_order_or_404(order_id)
    method = request.form.get("payment_method")
    if order["status"] != PENDING:
        flash("This order is not waiting for payment.", "error")
    elif method not in PAYMENT_METHODS:
        flash("Please choose a payment method.", "error")
    else:
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "UPDATE orders SET payment_status = 'PAID', payment_method = %s, "
            "paid_at = %s, status = %s WHERE id = %s",
            (method, datetime.now(), CONFIRMED, order_id),
        )
        log_status(cur, order_id, CONFIRMED, f"Paid via {method}")
        db.commit()
        cur.close()
        flash(f"Payment received via {method}. Order confirmed!", "success")
    return redirect(request.referrer or url_for("view_order", order_id=order_id))


@app.post("/order/<int:order_id>/next")
def next_status(order_id):
    """Prepare Order -> Order Ready -> Order Completed."""
    order = get_order_or_404(order_id)
    step = NEXT_STEP.get(order["status"])
    if step:
        new_status = step[0]
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "UPDATE orders SET status = %s, completed_at = %s WHERE id = %s",
            (new_status, datetime.now() if new_status == COMPLETED else None, order_id),
        )
        log_status(cur, order_id, new_status)
        db.commit()
        cur.close()
    return redirect(request.referrer or url_for("view_order", order_id=order_id))


if __name__ == "__main__":
    app.run(debug=True)