from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from database import get_connection # Assuming this returns a connection object
from utils import send_email # Assuming this function is defined elsewhere
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import datetime





user_bp = Blueprint('user', __name__, template_folder='templates')

UPLOAD_FOLDER = 'static/images/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ADMIN_EMAIL = "studentjntuh3@gmail.com" # Make sure this is configured correctly

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Existing User Authentication Routes (No changes here) ---
@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('Email already registered.', 'warning')
                    return redirect(url_for('user.register'))

                cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                               (name, email, hashed_password))
                connection.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('user.login'))
        except Exception as e:
            flash(f'Registration error: {e}', 'danger')
            if connection: connection.rollback()
        finally:
            if connection: connection.close()
        return redirect(url_for('user.register'))
    return render_template('user/register.html')

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        connection = get_connection()
        user = None
        try:
            with connection.cursor(dictionary=True) as cursor: # Assuming dictionary=True for easier access
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
        except Exception as e:
            flash(f'Login error: {e}', 'danger')
        finally:
            if connection: connection.close()

        if user and check_password_hash(user['password'], password): # Access by column name
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash('Logged in successfully.', 'success')
            return redirect(url_for('home')) # Assuming 'home' is your main page after login
        else:
            flash('Invalid email or password.', 'danger')
            # No redirect here, let it re-render the login form
    return render_template('user/login.html')


@user_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('user.login'))

# --- Existing Add Lost Item Route (No major changes, but ensure 'found' status is handled) ---

@user_bp.route('/add-lost-item', methods=['GET', 'POST'])
def add_lost_item():
    if 'user_id' not in session:
        if request.method == 'POST': # For AJAX/fetch calls
            return jsonify({'status': 'error', 'message': 'Authentication required.'}), 401
        flash('Please log in to report an item.', 'warning')
        return redirect(url_for('user.login'))

    if request.method == 'POST':
        # --- Get form data ---
        name = request.form.get('name', session.get('user_name', ''))
        roll_no = request.form.get('roll_no')
        phone = request.form.get('phone')
        product = request.form.get('product_name')
        department = request.form.get('department')
        location_found = request.form.get('location_found')
        description = request.form.get('description')
        item_type_status = request.form.get('item_status') # 'lost' or 'found'
        image = request.files.get('image')

        # --- Basic Validation ---
        required_fields = {'name': name, 'product_name': product, 'item_status': item_type_status, 'location_found': location_found, 'description': description, 'department': department, 'roll_no':roll_no, 'phone':phone}
        missing = [field_name for field_name, val in required_fields.items() if not val]
        if image is None or image.filename == '': # Image is also required based on your HTML
            missing.append('image')

        if missing:
            # For image specifically, your HTML has 'required', so it should be there
            # if 'image' in missing and (image is None or image.filename == ''):
            #    return jsonify({'status': 'error', 'message': 'Image is required.'}), 400

            return jsonify({'status': 'error', 'message': f"Missing required fields: {', '.join(missing)}"}), 400

        # --- Image Handling ---
        filename = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            try:
                # Ensure UPLOAD_FOLDER is accessible and correctly defined relative to app root in config
                # If UPLOAD_FOLDER is defined in app.config, use current_app.config['UPLOAD_FOLDER']
                # For this example, let's assume UPLOAD_FOLDER is relative to the project root where static is.
                # This path construction might need adjustment based on how UPLOAD_FOLDER is truly configured in your app.
                # The one in your user_bp is fine if your app's root is one level above 'user' directory.
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                image_folder_path = os.path.join(project_root, UPLOAD_FOLDER)
                
                if not os.path.exists(image_folder_path):
                    os.makedirs(image_folder_path, exist_ok=True)
                
                image_path = os.path.join(image_folder_path, filename)
                image.save(image_path)
            except Exception as e:
                # current_app.logger.error(f"Image save error: {e}") # Requires app context or pass logger
                print(f"Image save error: {e}") # For dev
                return jsonify({'status': 'error', 'message': f'Error saving image: {e}'}), 500
        elif image and not allowed_file(image.filename):
            return jsonify({'status': 'error', 'message': 'Invalid image file type. Allowed: png, jpg, jpeg, gif.'}), 400
        # If image is required and not provided (already checked above), but as a safeguard:
        elif not image and 'image' in missing: # This condition should have been caught by 'missing' check
             return jsonify({'status': 'error', 'message': 'Image is required.'}), 400


        # --- Database Operation ---
        connection = None # Initialize connection to None
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO lost_items 
                    (user_id, name, roll_no, phone, product_name, department, location_found, description, image_filename, status, verification_status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'unverified', NOW(), NOW())
                """, (
                    session['user_id'], name, roll_no or None, phone or None, product, department or None,
                    location_found, description or None, filename, item_type_status
                ))
                connection.commit()
            
            # Determine redirect URL for the frontend based on item_type_status
            redirect_url = ''
            if item_type_status == 'lost':
                redirect_url = url_for('user.view_lost_items')
            else: # 'found'
                redirect_url = url_for('user.view_found_items')

            return jsonify({
                'status': 'success', 
                'message': f'{item_type_status.capitalize()} item reported and awaiting verification.',
                'redirect_url': redirect_url
            }), 200

        except Exception as err:
            if connection:
                connection.rollback()
            # current_app.logger.error(f"Database error: {err}") # Requires app context
            print(f"Database error: {err}") # For dev
            return jsonify({'status': 'error', 'message': f'Database error: {err}'}), 500
        finally:
            if connection and connection.is_connected(): # Check if connection is active before closing
                connection.close()
        
        # This fallback should ideally not be reached if all paths return jsonify
        return jsonify({'status': 'error', 'message': 'An unexpected error occurred at the end of POST processing.'}), 500

    # For GET request, render the template as before
    return render_template('user/add_lost_item.html')
# --- Lost Item Flow (item starts as 'lost') ---
@user_bp.route('/view-lost-items')
def view_lost_items():
    if 'user_id' not in session:
        flash('Please log in to view items.', 'warning')
        return redirect(url_for('user.login'))

    current_user_id = session['user_id']
    connection = get_connection()
    items = []
    try:
        with connection.cursor(dictionary=True) as cursor:
            sql = """
                SELECT 
                    li.*, 
                    reporter.name AS reporter_name, /* This is the original owner */
                    reporter.email AS reporter_email,
                    finder.name AS finder_name, /* This is the user who found the lost item */
                    finder.email AS finder_email
                FROM lost_items li
                JOIN users reporter ON li.user_id = reporter.id
                LEFT JOIN users finder ON li.finder_user_id = finder.id
                WHERE 
                    li.verification_status = 'verified' 
                    AND li.archived = 0 /* Exclude archived items */
                    AND (li.status = 'lost' OR li.status = 'waiting_for_confirmation' OR li.status = 'resolved') 
                    /* We want to see lost items, those waiting for handover, and resolved ones before archiving */
                ORDER BY li.created_at DESC
            """
            cursor.execute(sql)
            items = cursor.fetchall()
    except Exception as e:
        flash(f"Error fetching lost items: {e}", "danger")
    finally:
        if connection: connection.close()
    return render_template('user/view_lost_items.html', items=items, current_user_id=current_user_id)

@user_bp.route('/report_item_as_found/<int:item_id>', methods=['POST'])
def report_item_as_found(item_id):
    if 'user_id' not in session:
        flash('Please log in to report a found item.', 'warning')
        return redirect(url_for('user.login'))

    finder_user_id = session['user_id']
    connection = get_connection()
    cursor = connection.cursor()

    # ✅ Get owner ID and item name from lost_items
    cursor.execute("SELECT user_id, product_name FROM lost_items WHERE id = %s", (item_id,))
    result = cursor.fetchone()

    if not result:
        flash('Item not found.', 'danger')
        cursor.close()
        connection.close()
        return redirect(url_for('user.view_lost_items'))

    owner_user_id, product_name = result

    # ✅ Update lost_items table
    cursor.execute("""
        UPDATE lost_items 
        SET status = 'waiting_for_confirmation', 
            finder_user_id = %s, 
            updated_at = NOW()
        WHERE id = %s
    """, (finder_user_id, item_id))
    connection.commit()

    # ✅ Insert claim into claims table
    cursor.execute("""
        INSERT INTO claims (
            item_id,
            claimer_user_id,
            claim_date,
            status,
            reporter_confirmed,
            claimer_confirmed,
            closed,
            wrong_claimer_reporter,
            wrong_claimer_claimer
        ) VALUES (%s, %s, NOW(), 'pending', 0, 0, 0, 0, 0)
    """, (item_id, finder_user_id))
    connection.commit()

    # ✅ Fetch owner's email
    cursor.execute("SELECT email FROM users WHERE id = %s", (owner_user_id,))
    owner_result = cursor.fetchone()

    if owner_result:
        owner_email = owner_result[0]
        subject = "Someone found your lost item!"
        message = f"""
Hello,

Good news! A user has reported finding your lost item: '{product_name}'.
Please log in to confirm and proceed with the handover process.

Thank you,
Lost & Found Team
        """.strip()
        send_email(owner_email, subject, message)

    cursor.close()
    connection.close()

    flash("Thank you for reporting this item as found. The owner has been notified.", 'success')
    return redirect(url_for('user.view_lost_items'))


# ✅ Owner confirms receipt
@user_bp.route('/confirm_receipt_from_finder/<int:item_id>', methods=['POST'])
def confirm_receipt_from_finder(item_id):
    if 'user_id' not in session:
        flash('Please log in to confirm receipt.', 'warning')
        return redirect(url_for('user.login'))

    current_user_id = session['user_id']
    connection = get_connection()

    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM lost_items WHERE id = %s AND user_id = %s", (item_id, current_user_id))
            item = cursor.fetchone()

            if not item:
                flash('Item not found or you are not authorized.', 'danger')
                return redirect(url_for('user.view_lost_items'))

            if item['status'] != 'waiting_for_confirmation':
                flash('Action cannot be performed on this item status.', 'warning')
                return redirect(url_for('user.view_lost_items'))

            # ✅ Update lost_items
            cursor.execute("""
                UPDATE lost_items 
                SET received_confirmed_by_reporter = 1, updated_at = NOW() 
                WHERE id = %s
            """, (item_id,))

            # ✅ Update claims
            cursor.execute("""
                UPDATE claims 
                SET reporter_confirmed = 1 
                WHERE item_id = %s AND closed = 0
            """, (item_id,))

            if item['handed_confirmed_by_finder']:
                cursor.execute("""
                    UPDATE lost_items 
                    SET status = 'resolved', updated_at = NOW() 
                    WHERE id = %s
                """, (item_id,))

                flash('Receipt confirmed! The item handover is complete and resolved.', 'success')

                # ✅ Notify Admin
                cursor.execute("""
                    SELECT li.product_name, owner.name as owner_name, finder.name as finder_name
                    FROM lost_items li
                    JOIN users owner ON li.user_id = owner.id
                    LEFT JOIN users finder ON li.finder_user_id = finder.id 
                    WHERE li.id = %s
                """, (item_id,))
                details = cursor.fetchone()

                admin_subject = f"Item Resolved: '{details['product_name']}' (Lost Item Flow)"
                admin_body = (f"Item '{details['product_name']}' (ID: {item_id}), lost by {details['owner_name']} and found by {details['finder_name']}, "
                              f"has been resolved. Both parties confirmed. Status: 'resolved'.")
                send_email(ADMIN_EMAIL, admin_subject, admin_body)
            else:
                flash('Receipt confirmed. Waiting for the finder to confirm handover.', 'info')

            connection.commit()

    except Exception as e:
        if connection: connection.rollback()
        flash(f'An error occurred: {e}', 'danger')
    finally:
        if connection: connection.close()

    return redirect(url_for('user.view_lost_items'))


# ✅ Finder confirms handover
@user_bp.route('/confirm_handover_to_owner/<int:item_id>', methods=['POST'])
def confirm_handover_to_owner(item_id):
    if 'user_id' not in session:
        flash('Please log in to confirm handover.', 'warning')
        return redirect(url_for('user.login'))

    current_user_id = session['user_id']
    connection = get_connection()

    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM lost_items WHERE id = %s AND finder_user_id = %s", (item_id, current_user_id))
            item = cursor.fetchone()

            if not item:
                flash('Item not found or you are not authorized.', 'danger')
                return redirect(url_for('user.view_lost_items'))

            if item['status'] != 'waiting_for_confirmation':
                flash('Action cannot be performed on this item status.', 'warning')
                return redirect(url_for('user.view_lost_items'))

            # ✅ Update lost_items
            cursor.execute("""
                UPDATE lost_items 
                SET handed_confirmed_by_finder = 1, updated_at = NOW() 
                WHERE id = %s
            """, (item_id,))

            # ✅ Update claims
            cursor.execute("""
                UPDATE claims 
                SET claimer_confirmed = 1 
                WHERE item_id = %s AND closed = 0
            """, (item_id,))

            if item['received_confirmed_by_reporter']:
                cursor.execute("""
                    UPDATE lost_items 
                    SET status = 'resolved', updated_at = NOW() 
                    WHERE id = %s
                """, (item_id,))

                flash('Handover confirmed! The item handover is complete and resolved.', 'success')

                # ✅ Notify Admin
                cursor.execute("""
                    SELECT li.product_name, owner.name as owner_name, finder.name as finder_name
                    FROM lost_items li
                    JOIN users owner ON li.user_id = owner.id
                    LEFT JOIN users finder ON li.finder_user_id = finder.id 
                    WHERE li.id = %s
                """, (item_id,))
                details = cursor.fetchone()

                admin_subject = f"Item Resolved: '{details['product_name']}' (Lost Item Flow)"
                admin_body = (f"Item '{details['product_name']}' (ID: {item_id}), lost by {details['owner_name']} and found by {details['finder_name']}, "
                              f"has been resolved. Both parties confirmed. Status: 'resolved'.")
                send_email(ADMIN_EMAIL, admin_subject, admin_body)
            else:
                flash('Handover confirmed. Waiting for the owner to confirm receipt.', 'info')

            connection.commit()

    except Exception as e:
        if connection: connection.rollback()
        flash(f'An error occurred: {e}', 'danger')
    finally:
        if connection: connection.close()

    return redirect(url_for('user.view_lost_items'))

# --- Found Item Flow (item starts as 'found', then claimed) ---
@user_bp.route('/view-found-items')
def view_found_items():
    if 'user_id' not in session:
        flash('Please log in to view found items.', 'warning')
        return redirect(url_for('user.login'))

    current_user_id = session['user_id']
    connection = get_connection()
    items_data = []
    try:
        with connection.cursor(dictionary=True) as cursor:
            # Fetch found items and their claim status if any
            # Items reported as 'found' initially, or that are 'claim_requested', or 'returned_to_claimer'
            cursor.execute("""
                SELECT 
                    li.*, 
                    reporter.name AS reporter_name, /* User who reported the item found */
                    reporter.email AS reporter_email,
                    c.id AS claim_id,
                    c.claimer_user_id,
                    cu.name AS claimer_name, /* User who claimed the item */
                    c.reporter_confirmed AS claim_reporter_confirmed,
                    c.claimer_confirmed AS claim_claimer_confirmed,
                    c.closed AS claim_closed
                FROM lost_items li
                JOIN users reporter ON li.user_id = reporter.id /* li.user_id is the finder */
                LEFT JOIN claims c ON li.id = c.item_id AND c.closed = 0 /* Only active or pending claims */
                LEFT JOIN users cu ON c.claimer_user_id = cu.id
                WHERE li.verification_status = 'verified' 
                    AND li.archived = 0 /* Exclude archived items */
                    AND (li.status = 'found' OR li.status = 'claim_requested' OR li.status = 'returned_to_claimer')
                ORDER BY li.created_at DESC
            """)
            items_data = cursor.fetchall()
    except Exception as e:
        flash(f"Error fetching found items: {e}", "danger")
    finally:
        if connection: connection.close()
    return render_template('user/view_found_items.html', items=items_data, current_user_id=current_user_id)

  # User claims an item that was 'found'
import datetime # Make sure this is at the top of your user_bp.py file

# ... (other imports, send_email function, ADMIN_EMAIL, etc.)
@user_bp.route('/claim-item/<int:item_id>', methods=['POST'])
def claim_item(item_id):
    if 'user_id' not in session:
        flash("Please log in to claim an item.", "warning")
        return redirect(url_for('user.login'))

    claimer_user_id = session['user_id']
    connection = get_connection()

    try:
        with connection.cursor(dictionary=True) as cursor:
            # 1. Check if item exists
            cursor.execute("SELECT * FROM lost_items WHERE id = %s", (item_id,))
            item = cursor.fetchone()
            print("Item found:", item)
            if not item:
                flash("Item not found.", "danger")
                return redirect(url_for('user.view_found_items'))

            # 2. Check if claiming own item
            if item['user_id'] == claimer_user_id:
                flash("You cannot claim your own item.", "warning")
                return redirect(url_for('user.view_found_items'))

            # 3. Ensure verified and eligible
            if item['verification_status'] != 'verified' or item['status'] not in ['found', 'waiting_for_confirmation']:
                flash("Item is not eligible for claim.", "warning")
                return redirect(url_for('user.view_found_items'))

            # 4. Check for existing active claim
            cursor.execute("SELECT * FROM claims WHERE item_id = %s AND closed = 0", (item_id,))
            existing = cursor.fetchone()
            print("Existing claim found?", existing)
            if existing:
                flash("Item already has an active claim.", "warning")
                return redirect(url_for('user.view_found_items'))

            # 5. INSERT new claim
            print("Inserting claim now...")
            cursor.execute("""
                INSERT INTO claims (
                    item_id, claimer_user_id, claim_date, status,
                    reporter_confirmed, claimer_confirmed, closed,
                    wrong_claimer_reporter, wrong_claimer_claimer
                ) VALUES (%s, %s, NOW(), 'pending', 0, 0, 0, 0, 0)
            """, (item_id, claimer_user_id))
            print("Claim inserted successfully.")

            # 6. Update item status
            cursor.execute("UPDATE lost_items SET status = 'claim_requested', updated_at = NOW() WHERE id = %s", (item_id,))
            print("Item status updated.")

            connection.commit()
            print("Transaction committed.")

            flash("Claim submitted successfully!", "success")

    except Exception as e:
        if connection:
            connection.rollback()
        print("⚠️ Error during claim:", e)
        flash("Something went wrong while submitting your claim.", "danger")

    finally:
        if connection:
            connection.close()

    return redirect(url_for('user.view_found_items'))

@user_bp.route('/confirm_receipt_by_claimer/<int:claim_id>', methods=['POST'])
def confirm_receipt_by_claimer(claim_id):
    if 'user_id' not in session:
        flash("Please log in.", "warning")
        return redirect(url_for('user.login'))

    current_user_id = session['user_id']
    connection = get_connection()

    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT c.*, li.id as item_id, li.product_name, li.user_id as original_reporter_id
                FROM claims c
                JOIN lost_items li ON c.item_id = li.id
                WHERE c.id = %s AND c.claimer_user_id = %s
            """, (claim_id, current_user_id))
            claim = cursor.fetchone()

            if not claim:
                flash("Claim not found or permission denied.", "danger")
                return redirect(url_for('user.view_found_items'))

            if claim['closed']:
                flash("This claim is already closed.", "info")
                return redirect(url_for('user.view_found_items'))

            # ✅ Just update claimer confirmation — do NOT close
            cursor.execute("UPDATE claims SET claimer_confirmed = 1 WHERE id = %s", (claim_id,))
            connection.commit()

            if claim['reporter_confirmed']:
                flash("Receipt confirmed! Both parties have confirmed. Awaiting admin to close the case.", "success")
            else:
                flash("Receipt confirmed. Waiting for the original reporter to confirm the handover.", "info")

    except Exception as e:
        if connection: connection.rollback()
        flash(f"Error confirming receipt: {e}", "danger")
    finally:
        if connection: connection.close()

    return redirect(url_for('user.view_found_items'))
@user_bp.route('/confirm_handover_by_reporter/<int:claim_id>', methods=['POST'])
def confirm_handover_by_reporter(claim_id):
    if 'user_id' not in session:
        flash("Please log in.", "warning")
        return redirect(url_for('user.login'))

    current_user_id = session['user_id']
    connection = get_connection()

    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT c.*, li.id as item_id, li.product_name, li.user_id as original_reporter_id,
                       claimer_users.name as claimer_name
                FROM claims c
                JOIN lost_items li ON c.item_id = li.id
                JOIN users claimer_users ON c.claimer_user_id = claimer_users.id
                WHERE c.id = %s AND li.user_id = %s
            """, (claim_id, current_user_id))
            claim = cursor.fetchone()

            if not claim:
                flash("Claim not found or permission denied.", "danger")
                return redirect(url_for('user.view_found_items'))

            if claim['closed']:
                flash("This claim is already closed.", "info")
                return redirect(url_for('user.view_found_items'))

            # ✅ Just update reporter confirmation — do NOT close
            cursor.execute("UPDATE claims SET reporter_confirmed = 1 WHERE id = %s", (claim_id,))
            connection.commit()

            if claim['claimer_confirmed']:
                flash("Handover confirmed! Both parties have confirmed. Awaiting admin to close the case.", "success")
            else:
                flash("Handover confirmed. Waiting for the claimer to confirm receipt.", "info")

    except Exception as e:
        if connection: connection.rollback()
        flash(f"Error confirming handover: {e}", "danger")
    finally:
        if connection: connection.close()

    return redirect(url_for('user.view_found_items'))

@user_bp.route('/report_wrong_item/<int:claim_id>/<role>', methods=['POST'])
def report_wrong_item(claim_id, role):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch claim
    cursor.execute("SELECT * FROM claims WHERE id = %s", (claim_id,))
    current_claim = cursor.fetchone()

    if not current_claim:
        flash("Claim not found.", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for('main.index'))  # or your main page

    # Fetch found item related to the claim
    cursor.execute("SELECT * FROM lost_items WHERE id = %s", (current_claim['item_id'],))
    found_item = cursor.fetchone()

    if not found_item:
        flash("Associated item not found.", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for('user.view_found_items'))

    # Update claim flags based on role
    if role == 'claimer':
        cursor.execute(
            "UPDATE claims SET wrong_claimer_claimer = %s WHERE id = %s",
            (True, claim_id)
        )
        user_who_reported = "Claimer"
        other_party_name = "Reporter"

    elif role == 'reporter':
        cursor.execute(
            "UPDATE claims SET wrong_claimer_reporter = %s WHERE id = %s",
            (True, claim_id)
        )
        user_who_reported = "Reporter"
        other_party_name = "Claimer"
    else:
        flash("Invalid role specified.", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for('user.view_found_items'))

    conn.commit()

    # Re-fetch claim to check both flags
    cursor.execute("SELECT * FROM claims WHERE id = %s", (claim_id,))
    current_claim = cursor.fetchone()

    
    if current_claim['wrong_claimer_claimer'] and current_claim['wrong_claimer_reporter']:
    # Both parties agree - update lost_items and close claim
        cursor.execute(
        "UPDATE lost_items SET status = %s WHERE id = %s",
        ('found', found_item['id'])
    )
        cursor.execute(
        "UPDATE claims SET closed = %s, status = %s WHERE id = %s",
        (True, 'closed', current_claim['id'])
    )
        conn.commit()


        # Send admin notification email
        subject = f"Found Item Claim #{claim_id} Resolved: Mismatch"
        body = (f"The claim (ID: {claim_id}) for Found Item (ID: {found_item['id']}, Name: {found_item['product_name']}) "
                f"has been marked as a mismatch by both the original reporter and the claimer.\n\n"
                f"The item '{found_item['product_name']}' (ID: {found_item['id']}) has been made available again.\n"
                f"No further action is required unless review is desired.")
        admin_email = "studentjntuh3@gmail.com"
        try:
            send_email(admin_email, subject, body)
            print(f"Admin notification sent for claim {claim_id} mismatch.")
        except Exception as e:
            print(f"Failed to send admin email: {e}")

        flash(f"Mismatch confirmed by both parties. The item '{found_item['product_name']}' is now available again.", "success")
    else:
        flash(f"Your report has been recorded. Waiting for {other_party_name} to confirm.", "info")

    cursor.close()
    conn.close()
    return redirect(url_for('user.view_found_items'))

@user_bp.route('/report_wrong_lost_item/<int:item_id>/<role>', methods=['POST'])
def report_wrong_lost_item(item_id, role):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch claim associated with this item (consider adding user filter if needed)
    cursor.execute("SELECT * FROM claims WHERE item_id = %s", (item_id,))
    claim = cursor.fetchone()

    if not claim:
        flash("Claim record not found for this item.", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for('user.view_lost_items'))

    # Fetch lost item
    cursor.execute("SELECT * FROM lost_items WHERE id = %s", (item_id,))
    lost_item = cursor.fetchone()

    if not lost_item or lost_item['status'] != 'waiting_for_confirmation':
        flash("Lost item not found or not in a state to report mismatch.", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for('user.view_lost_items'))

    # Fetch owner and finder user info
    cursor.execute("SELECT * FROM users WHERE id = %s", (lost_item['user_id'],))
    owner = cursor.fetchone()

    finder_user_id = lost_item.get('finder_user_id')
    if finder_user_id:
        cursor.execute("SELECT * FROM users WHERE id = %s", (finder_user_id,))
        finder = cursor.fetchone()
    else:
        finder = None

    if not owner or not finder:
        flash("Owner or Finder information missing.", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for('user.view_lost_items'))

    if role == 'claimer':
        cursor.execute(
            "UPDATE claims SET wrong_claimer_claimer = %s WHERE id = %s",
            (True, claim['id'])
        )
        other_party_name = finder['name']
    elif role == 'reporter':
        cursor.execute(
            "UPDATE claims SET wrong_claimer_reporter = %s WHERE id = %s",
            (True, claim['id'])
        )
        other_party_name = owner['name']
    else:
        flash("Invalid role specified.", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for('user.view_lost_items'))

    conn.commit()

    # Re-fetch claim to check flags
    cursor.execute("SELECT * FROM claims WHERE id = %s", (claim['id'],))
    updated_claim = cursor.fetchone()

    if updated_claim['wrong_claimer_claimer'] and updated_claim['wrong_claimer_reporter']:
        cursor.execute(
            """
            UPDATE lost_items SET
                status = %s,
                finder_user_id = NULL,
                handed_confirmed_by_finder = 0,
                received_confirmed_by_reporter = 0
            WHERE id = %s
            """,
            ('lost', item_id)
        )
        cursor.execute(
            """
            UPDATE claims SET
                wrong_claimer_claimer = 0,
                wrong_claimer_reporter = 0,
                status = 'closed',
                closed = 1
            WHERE id = %s
            """,
            (claim['id'],)
        )
        conn.commit()

        # Send admin notification
        subject = f"Lost Item (ID: {item_id}) 'Found' Interaction Resolved: Mismatch"
        body = (
            f"The 'found' interaction for Lost Item (ID: {item_id}, Name: {lost_item['product_name']}) "
            f"has been marked as a mismatch by both the Owner ({owner['name']}) "
            f"and the Finder ({finder['name']}).\n\n"
            f"The item has been reverted to 'lost' status and finder info cleared."
        )
        admin_email = "studentjntuh3@gmail.com"
        try:
            send_email(admin_email, subject, body)
            print(f"Admin notification sent for lost item {item_id} mismatch.")
        except Exception as e:
            print(f"Failed to send admin email: {e}")

        flash(f"Mismatch confirmed by both parties. The item '{lost_item['product_name']}' is now marked as 'lost' again.", "success")
    else:
        flash(f"Your report has been recorded. Waiting for {other_party_name} to confirm.", "info")

    cursor.close()
    conn.close()
    return redirect(url_for('user.view_lost_items'))
from flask import session  # make sure this is imported

@user_bp.route('/contact_admin', methods=['GET', 'POST'])
def contact_admin():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        user_id = session.get('user_id')

        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO feedback (user_id, name, email, subject, message)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, name, email, subject, message))
                connection.commit()

            admin_email = "studentjntuh3@gmail.com"
            mail_subject = f"New Query: {subject}"
            mail_body = f"From: {name} <{email}>\n\n{message}"
            send_email(admin_email, mail_subject, mail_body)

            session['show_feedback_success'] = True  # ✅ set flag for SweetAlert
        except Exception as e:
            flash(f"Something went wrong: {e}", "danger")
        finally:
            connection.close()

        return redirect(url_for('user.contact_admin'))  # PRG pattern

    return render_template('contact_admin.html')
