# app.py

from coletor_dados_mlb import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)