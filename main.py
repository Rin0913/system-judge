from app import initialize_app
from config import get_runtime_config

app = initialize_app(get_runtime_config())

if __name__ == '__main__':
    app.run(host='0.0.0.0', use_reloader=False)
