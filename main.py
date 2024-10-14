from app import initialize_app

app = initialize_app('Development')

if __name__ == '__main__':
    app.run(host='0.0.0.0',)
