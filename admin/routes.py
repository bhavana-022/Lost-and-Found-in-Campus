from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_connection

admin_bp = Blueprint('admin', __name__, template_folder='templates')

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

# Admin login
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_id'] = username
            flash('Logged in as Admin.', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('admin/login.html')

# Admin logout
@admin_bp.route('/logout')
def logout():
    session.pop('admin_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.login'))

# Admin dashboard
@admin_bp.route('/dashboard')
def dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin.login'))

    connection = get_connection()
    items = []
    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM lost_items WHERE archived = FALSE ORDER BY id DESC")
            items = cursor.fetchall()
    except Exception as e:
        flash(f'Error fetching items: {e}', 'danger')
    finally:
        if connection: connection.close()
    return render_template('admin/dashboard.html', items=items)

# Verified items
@admin_bp.route('/verified-items')
def verified_items():
    if 'admin_id' not in session:
        return redirect(url_for('admin.login'))

    connection = get_connection()
    items = []
    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM lost_items WHERE verification_status = 'verified' AND archived = FALSE ORDER BY id DESC")
            items = cursor.fetchall()
    except Exception as e:
        flash(f'Error fetching verified items: {e}', 'danger')
    finally:
        if connection: connection.close()
    return render_template('admin/verified_items.html', items=items)

# Verify item
@admin_bp.route('/verify-item/<int:item_id>', methods=['POST'])
def verify_item(item_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin.login'))

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE lost_items
                SET verification_status = 'verified', updated_at = NOW()
                WHERE id = %s
            """, (item_id,))
            connection.commit()
        flash('Item marked as verified.', 'success')
    except Exception as e:
        connection.rollback()
        flash(f'Error verifying item: {e}', 'danger')
    finally:
        if connection: connection.close()
    return redirect(url_for('admin.dashboard'))

# Delete item
@admin_bp.route('/delete-item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin.login'))

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM lost_items WHERE id = %s", (item_id,))
            connection.commit()
        flash('Item deleted successfully.', 'success')
    except Exception as e:
        connection.rollback()
        flash(f'Error deleting item: {e}', 'danger')
    finally:
        if connection: connection.close()
    return redirect(url_for('admin.verified_items'))

# Active claims
@admin_bp.route('/claims')
def view_claims():
    if 'admin_id' not in session:
        flash("Please log in as admin.", "warning")
        return redirect(url_for('admin.login'))

    connection = get_connection()
    active_claims = []
    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT c.id AS claim_id, li.id AS item_id, li.product_name, li.image_filename,
                       li.status AS item_status, li.description, li.created_at AS item_reported_at,
                       cu.name AS claimer_name, cu.email AS claimer_email,
                       ru.name AS reporter_name, ru.email AS reporter_email,
                       c.claim_date, c.status AS claim_internal_status,
                       c.reporter_confirmed, c.claimer_confirmed, c.closed
                FROM claims c
                JOIN lost_items li ON c.item_id = li.id
                JOIN users cu ON c.claimer_user_id = cu.id
                JOIN users ru ON li.user_id = ru.id
                WHERE c.closed = FALSE
                ORDER BY c.claim_date DESC
            """)
            active_claims = cursor.fetchall()
    except Exception as e:
        flash(f'Error fetching active claims: {e}', 'danger')
    finally:
        if connection: connection.close()
    return render_template('admin/view_claims.html', claims=active_claims)

# Archived claims
@admin_bp.route('/archived-claims')
def view_archived_claims():
    if 'admin_id' not in session:
        flash("Please log in as admin.", "warning")
        return redirect(url_for('admin.login'))

    connection = get_connection()
    archived_claims = []
    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT c.id AS claim_id, li.id AS item_id, li.product_name, li.image_filename,
                       li.status AS item_status, li.description, li.created_at AS item_reported_at,
                       cu.name AS claimer_name, cu.email AS claimer_email,
                       ru.name AS reporter_name, ru.email AS reporter_email,
                       c.claim_date, c.status AS claim_internal_status,
                       c.reporter_confirmed, c.claimer_confirmed, c.closed
                FROM claims c
                JOIN lost_items li ON c.item_id = li.id
                JOIN users cu ON c.claimer_user_id = cu.id
                JOIN users ru ON li.user_id = ru.id
                WHERE c.closed = TRUE
                ORDER BY c.claim_date DESC
            """)
            archived_claims = cursor.fetchall()
    except Exception as e:
        flash(f'Error fetching archived claims: {e}', 'danger')
    finally:
        if connection: connection.close()
    return render_template('admin/archived_claims.html', claims=archived_claims)

# Close claim
@admin_bp.route('/close-claim/<int:claim_id>', methods=['POST'])
def close_claim(claim_id):
    if 'admin_id' not in session:
        flash("Please log in as admin.", "warning")
        return redirect(url_for('admin.login'))

    connection = get_connection()
    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT c.item_id, li.product_name, ru.name AS reporter_name, ru.email AS reporter_email,
                       cu.name AS claimer_name, cu.email AS claimer_email
                FROM claims c
                JOIN lost_items li ON c.item_id = li.id
                JOIN users ru ON li.user_id = ru.id
                JOIN users cu ON c.claimer_user_id = cu.id
                WHERE c.id = %s AND c.reporter_confirmed = TRUE AND c.claimer_confirmed = TRUE AND c.closed = FALSE
            """, (claim_id,))
            claim_details = cursor.fetchone()

            if not claim_details:
                flash("Cannot close claim: It's not fully confirmed by both parties, or it's already closed.", "warning")
                return redirect(url_for('admin.view_claims'))

            cursor.execute("UPDATE claims SET closed = TRUE WHERE id = %s", (claim_id,))

            cursor.execute("""
                UPDATE lost_items
                SET archived = TRUE, status = 'returned_to_claimer_archived', updated_at = NOW()
                WHERE id = %s
            """, (claim_details['item_id'],))

            connection.commit()
            flash('Claim closed and item archived successfully.', 'success')
    except Exception as e:
        connection.rollback()
        flash(f'Error closing claim: {e}', 'danger')
    finally:
        if connection: connection.close()
    return redirect(url_for('admin.view_claims'))
