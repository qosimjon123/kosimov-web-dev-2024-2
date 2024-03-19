from flask import Flask, render_template, request, make_response
from checkNumber import valid_number


app = Flask(__name__)
application = app


@app.route('/')
def index():
    url = request.url
    return render_template('index.html', url=url)

@app.route('/args')
def args():
    return render_template('args.html')

@app.route('/headers')
def headers():
    return render_template('headers.html')

@app.route('/cookies')
def cookies():
    response = make_response(render_template('cookies.html'))
    if "User"  not in request.cookies:
        response.set_cookie("User","Hello World!")
    else:
        response.delete_cookie("User")
    return response




@app.route('/check_number', methods = ["POST", "GET"])
def check_number():
    category = ""
    if request.method == "POST":
        if request.form.get("number","") != "":
            value, text = valid_number(request.form.get("number"))
            category = "is-valid" if value else "is-invalid"
        return render_template("checkNumber.html", category = category, text=text)
    else:
        return render_template("checkNumber.html", category=category)



@app.route("/form", methods = ["POST", "GET"])
def form():
    return render_template("forms.html")

@app.route("/calc", methods = ["POST", "GET"])
def calc():
    res = 0
    error = ''
    if request.method == "POST":
        try:
            a = float(request.form['a'])
            op = request.form['operation']
            b = float(request.form['b'])
            match op:
                case '+':
                    res = a + b
                case '-':
                    res = a - b
                case '/':
                    res = a / b
                case '*':
                    res = a * b
        except ZeroDivisionError:
            error = 'Деление на 0 невозможно'
        except ValueError: 
            error = 'Неверный тип данных'
        
    return render_template("calc.html", res = res, error = error)


if __name__ == "__main__":
    app.run(debug = True)