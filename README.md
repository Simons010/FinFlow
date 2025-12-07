FinFlow is a modern financial management application that helps users track income, expenses, and monitor financial performance through an intuitive and responsive interface.

**🚀 Features**

💰 Income & expense tracking

📊 Interactive dashboard with summaries

📈 Monthly reports and trend charts

🎯 Customizable categories

🔍 Advanced search & filtering

🌙 Light/Dark mode

🔐 User authentication with isolated data

📱 Fully responsive interface

**🛠️ Tech Stack**
Component	Technology
Backend	Django 5.x
Frontend	Django Templates + Tailwind CSS
Database	SQLite (dev), PostgreSQL (prod)
Runtime	Python 3.11+
Build Tools	Node.js + npm


**⚡ Quick Start**
Prerequisites:
    Python 3.11+
    Node.js 18+
    pip

1. Clone the repository
git clone https://github.com/simons010/finflow.git
cd finflow

2. Set up a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt
npm install

4. Apply migrations
python manage.py migrate

5. Start development servers

Django:
python manage.py runserver


Tailwind (watch mode):
npm run tailwind:watch


Open http://localhost:8000

**📂 Project Structure**
finflow/
├── config/            # Project settings & URLs
├── finflow/           # Core app (models, views, URLs)
├── accounts/          # Authentication
├── templates/         # HTML templates
├── static/            # Static assets (CSS/JS/images)
├── manage.py          # Django CLI entry
├── requirements.txt   # Python dependencies
└── tailwind.config.js # Tailwind setup

Production configuration should rely on environment variables.

🧪 Development Commands
python manage.py makemigrations
python manage.py migrate
python manage.py test
python manage.py collectstatic
npm run tailwind:build

**📦 Deployment**

FinFlow supports various deployment environments including:

Traditional VPS (Nginx + Gunicorn)

Cloud hosting providers

Containerized deployments

See DEPLOYMENT.md for full details.

**🤝 Contributing**

Contributions are welcome!

Fork the repo

Create a feature branch

Commit changes with descriptive messages

Submit a pull request

**👥 Author**

Macharia Simon
