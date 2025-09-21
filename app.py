# import psycopg2
# from psycopg2 import sql

# # CHANGE: Replace with your Supabase connection details
# DB_URI = "postgresql://postgres:HOLYFUCKINGSHIT123@db.nzwplfahwbkefysxglrf.supabase.co:5432/postgres"

# try:
#     # Connect to the database
#     conn = psycopg2.connect(DB_URI)
#     cursor = conn.cursor()
    
#     # Test query
#     cursor.execute("SELECT NOW();")
#     result = cursor.fetchone()
#     print("Connection successful! Current time in DB:", result[0])
    
#     cursor.close()
#     conn.close()
# except Exception as e:
#     print("Connection failed:", e)



import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta

# CHANGE: Import SQLAlchemy for PostgreSQL
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # allows cross-origin requests so we can access it in our Flutter web app

# CHANGE: Use environment variable for DB URI or hardcode temporarily for testing
DB_URI = os.environ.get("DATABASE_URL", "postgresql://postgres:HOLYFUCKINGSHIT123@db.nzwplfahwbkefysxglrf.supabase.co:5432/postgres")
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # suppress warning


# CHANGE: Initialize SQLAlchemy
db = SQLAlchemy(app)
print(db)


# CHANGE: Define expenses model
class Expense(db.Model):
    __tablename__ = "expenses"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String)
    notes = db.Column(db.String)    

# CHANGE: Create tables (run once)
with app.app_context():
    db.create_all()

# ==================================================================================================================

# === Route: Add a new record ===
@app.route('/add', methods=['POST'])
def add_record():
    try:
        data = request.get_json()  # expects JSON like {"Date": "2025-09-21", "Category": "Food", "Amount": 15.5, "Payment_Method": "Card", "Notes": "bought burgers", "User_ID": "user@example.com"}
        
        # Validate required fields
        if not all(k in data for k in ("Date", "Category", "Amount", "User_ID")):
            return jsonify({"error": "Missing required fields"}), 400

        # CHANGE: Insert into PostgreSQL
        new_expense = Expense(
            user_id = data["User_ID"],
            date = datetime.strptime(data["Date"], "%Y-%m-%d").date(),
            category = data["Category"].strip().title(),
            amount = float(data["Amount"]),
            payment_method = data.get("Payment_Method", "").strip().title(),
            notes = data.get("Notes", "").strip()
        )
        db.session.add(new_expense)
        db.session.commit()

        return jsonify({"message": "Record added successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500





# === Route: Summary ===
@app.route('/summary')
def summary():
    try:
        days = int(request.args.get("days", 0))
        user_id = request.args.get("user_id", "")  # CHANGE: filter by user

        query = Expense.query.filter_by(user_id=user_id)
        
        if days in [7, 30]:
            cutoff = datetime.now().date() - timedelta(days=days)
            query = query.filter(Expense.date >= cutoff)
        
        expenses = query.all()
        
        # Total spent
        total_spent = sum(e.amount for e in expenses)
        
        # Total by category
        total_by_category = {}
        for e in expenses:
            cat = e.category
            total_by_category[cat] = total_by_category.get(cat, 0) + e.amount
        
        # Daily average
        dates = list(set(e.date for e in expenses))
        daily_avg = total_spent / len(dates) if dates else 0

        return jsonify({
            'total_spent': total_spent,
            'total_by_category': total_by_category,
            'daily_avg': daily_avg,
            'records_count': len(expenses)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500






# === Route: Trend data ===
@app.route('/trend')
def trend():
    try:
        days = int(request.args.get("days", 0))
        user_id = request.args.get("user_id", "")

        query = Expense.query.filter_by(user_id=user_id)
        if days in [7, 30]:
            cutoff = datetime.now().date() - timedelta(days=days)
            query = query.filter(Expense.date >= cutoff)
        
        expenses = query.all()
        trend_data = {}
        for e in expenses:
            trend_data[e.date] = trend_data.get(e.date, 0) + e.amount
        
        sorted_dates = sorted(trend_data.keys())
        amounts = [trend_data[d] for d in sorted_dates]

        return jsonify({
            'dates': [d.strftime("%Y-%m-%d") for d in sorted_dates],
            'amounts': amounts,
            'records_count': len(expenses)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500






# === Route: Prediction (placeholder) ===
@app.route('/prediction')
def prediction():
    try:
        days = int(request.args.get("days", 0))
        predictionPeriod = request.args.get('predictionPeriod', 'week')
        user_id = request.args.get("user_id", "")

        query = Expense.query.filter_by(user_id=user_id)
        if days in [7, 30]:
            cutoff = datetime.now().date() - timedelta(days=days)
            query = query.filter(Expense.date >= cutoff)

        expenses = query.all()

        # Average daily spend
        daily_totals = {}
        for e in expenses:
            daily_totals[e.date] = daily_totals.get(e.date, 0) + e.amount
        
        avg_daily = sum(daily_totals.values()) / len(daily_totals) if daily_totals else 0
        period_days = 7 if predictionPeriod == 'week' else 30
        forecast = avg_daily * period_days

        return jsonify({
            'predictionPeriod': predictionPeriod,
            'predicted_total': forecast,
            'records_count': len(expenses)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500




    


# Run Flask app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)