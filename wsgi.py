"""
Sash SMS — Production & Vercel WSGI Entrypoint
"""
import os
from app import create_app

config_name = os.environ.get('FLASK_ENV', 'production')
app = create_app(config_name)

if __name__ == "__main__":
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', '20168'))
    app.run(host=host, port=port)
