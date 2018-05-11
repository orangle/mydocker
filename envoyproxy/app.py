# coding:utf-8
import click
from flask import Flask

app = Flask(__name__)
greet = ""

@app.route('/')
def root():
    return greet 


@click.command()
@click.option("--port", default=10001, help="listen port")
@click.option("--hello", default="hello", help="echo content, default is hello")
def main(port, hello):
    global greet 
    greet = hello
    app.run(debug=True, port=port, host='0.0.0.0')

if __name__ == "__main__":
    main()