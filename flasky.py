import os
from flask_migrate import Migrate
from app import create_app, db


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db, render_as_batch=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
