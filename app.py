from routes import app



if __name__ == '__main__':
    app.run(debug=False)
    
app.static_folder = 'static' 

