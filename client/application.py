from app import create_app

app = create_app()

# Reading client application

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
