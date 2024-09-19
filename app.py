from routes import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)  # Cambia 5000 por el puerto que desees

app.static_folder = 'static'
