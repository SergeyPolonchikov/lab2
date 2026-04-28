from __future__ import annotations

import re

from flask import Flask, make_response, redirect, render_template, request, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"


ALLOWED_PHONE_CHARS_RE = re.compile(r"^[0-9\s().+\-]*$")


def validate_phone(phone_raw: str) -> tuple[bool, str | None, str]:
    phone = (phone_raw or "").strip()

    if not ALLOWED_PHONE_CHARS_RE.fullmatch(phone):
        return (
            False,
            "Недопустимый ввод. В номере телефона встречаются недопустимые символы.",
            phone,
        )

    digits = re.sub(r"\D", "", phone)

    # "номер должен содержать 11 цифр если он начинается с «+7» или «8»,
    # в остальных случаях – 10 цифр"
    requires_11 = phone.startswith("+7") or phone.startswith("8")
    expected_len = 11 if requires_11 else 10
    if len(digits) != expected_len:
        return (
            False,
            "Недопустимый ввод. Неверное количество цифр.",
            phone,
        )

    return True, None, digits


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/request")
def request_info():
    resp = make_response(
        render_template(
            "request.html",
            url_args=dict(request.args),
            headers=dict(request.headers),
            cookies=request.cookies,
        )
    )
    # Demo cookie so the "cookies" section is never empty on first visit.
    if "demo_cookie" not in request.cookies:
        resp.set_cookie("demo_cookie", "hello")
    return resp


@app.route("/login", methods=["GET", "POST"])
def login():
    submitted = None
    if request.method == "POST":
        submitted = {
            "username": request.form.get("username", ""),
            "password": request.form.get("password", ""),
        }
    return render_template("login.html", submitted=submitted, form_data=request.form)


@app.route("/phone", methods=["GET", "POST"])
def phone():
    value = ""
    is_valid = True
    error = None
    normalized = None

    if request.method == "POST":
        value = request.form.get("phone", "")
        is_valid, error, normalized = validate_phone(value)

    return render_template(
        "phone.html",
        value=value,
        is_valid=is_valid,
        error=error,
        normalized=normalized,
    )


@app.get("/set-cookie")
def set_cookie():
    resp = make_response(redirect(url_for("request_info")))
    resp.set_cookie("my_cookie", "value")
    return resp


if __name__ == "__main__":
    app.run(debug=True)
