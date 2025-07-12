# 🧳 Lost and Found in Campus – Flask Web App

A web app to report, track, and manage lost and found items within a college campus.  
Built using **Flask**, **MySQL**, and **Bootstrap**. Supports both **user and admin modules**, with real-time email notifications.

---

## 🚀 Features

### 👤 User
- Register/login
- Report lost/found items
- Claim found items
- Track claim status

### 🔐 Admin
- Approve/reject lost/found items
- Review and resolve claims
- Update item status (Resolved/Returned)
- Email communication with users

---

## 🛠 Tech Stack

| Tech          | Role                     |
|---------------|--------------------------|
| Python + Flask| Backend & routing        |
| MySQL         | Database                 |
| HTML/CSS/JS   | Frontend                 |
| Bootstrap     | Styling                  |
| Jinja2        | HTML templating          |
| SMTP (Gmail)  | Email notifications      |

---

## 🗂 Folder Structure

```text
lostt_and_foundd/
├── app.py               # Main entry point
├── config.py            # Config (reads from .env)
├── utils.py             # Email sending logic
├── database.py          # DB connection
├── templates/           # Jinja2 HTML templates
├── static/              # CSS, JS, images
├── admin/               # Admin routes
├── user/                # User routes
├── .env                 # Private env vars (not pushed)
├── .env.example         # Template for .env
├── requirements.txt     # Python dependencies
└── README.md            # You're here!
```
## 🔧 Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/bhavana-022/Lost-and-Found-in-Campus.git
cd Lost-and-Found-in-Campus
```
### 2. Create virtual environment (optional but recommended)

```bash
python -m venv venv
venv\Scripts\activate  # For Windows
```
### 3. Install dependencies

```bash
pip install -r requirements.txt
```
### 4. Create a `.env` file in the root directory

```env
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_gmail_app_password
💡 Use a Gmail App Password, not your actual email password.
```
### 5. Run the Flask application

```bash
python app.py
```
---

## 🌍 Deployment

You can deploy this project on platforms like:

- 🔗 [Render](https://render.com/)
- 💻 [PythonAnywhere](https://www.pythonanywhere.com/)
- ☁️ [Heroku](https://www.heroku.com/)

Want a guide? [Click here](https://render.com/docs/deploy-flask) or ask in Issues.

---

## 🧪 Testing

To run tests (if added), use:

```bash
pytest
```
---

## 📝 License

This project is open-source and intended for **educational use**.

Feel free to fork, customize, and use in your campus or academic projects.

---

## ✨ Credits

- 🧑‍💻 **Built by**: Bhavana  
- 🎓 **Final Year BTech – JNTUH (CSE-AIML)**  
- 🌐 **GitHub**: [@bhavana-022](https://github.com/bhavana-022)

