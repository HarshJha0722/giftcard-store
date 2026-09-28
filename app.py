from flask import Flask, render_template_string, abort
import qrcode
from io import BytesIO
import base64
from urllib.parse import quote

app = Flask(__name__)

UPI_ID = "Vagteshgheru@ybl"
STORE_NAME = "GiftCard Store"

PRODUCTS = {
    "amazon": {
        "name": "Amazon Gift Card",
        "emoji": "🛒",
        "color": "#ff9900"
    },
    "blinkit": {
        "name": "Blinkit Gift Card",
        "emoji": "⚡",
        "color": "#f7d600"
    },
    "flipkart": {
        "name": "Flipkart Gift Card",
        "emoji": "🛍️",
        "color": "#2874f0"
    },
    "google-play": {
        "name": "Google Play Gift Card",
        "emoji": "🎮",
        "color": "#34a853"
    }
}

AMOUNTS = list(range(500, 10001, 500))

STYLE = """
<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #080b12;
    color: #fff;
    font-family: Arial, sans-serif;
}

header {
    background: #121827;
    border-bottom: 1px solid #30394b;
    padding: 20px 12px;
    text-align: center;
    font-size: 23px;
    font-weight: bold;
    color: #ffd700;
}

.hero {
    text-align: center;
    padding: 35px 15px;
}

.hero h1 {
    font-size: 30px;
    margin: 10px 0;
}

.hero p {
    color: #aab3c5;
    line-height: 1.7;
}

.products {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
    padding: 15px;
    max-width: 850px;
    margin: auto;
}

.card {
    background: linear-gradient(145deg, #192337, #101521);
    border: 1px solid #30394b;
    border-radius: 18px;
    padding: 20px 12px;
    text-align: center;
    box-shadow: 0 8px 25px #0005;
}

.emoji {
    font-size: 48px;
    margin-bottom: 12px;
}

.card h3 {
    font-size: 17px;
    min-height: 40px;
}

.card p {
    color: #aab3c5;
    font-size: 14px;
}

button {
    background: linear-gradient(135deg, #ffe45c, #ffb800);
    color: #111;
    border: none;
    border-radius: 11px;
    padding: 14px 12px;
    font-weight: bold;
    font-size: 15px;
    width: 100%;
    margin-top: 12px;
    cursor: pointer;
}

button:active {
    transform: scale(.97);
}

.container {
    max-width: 700px;
    margin: auto;
    padding: 20px 15px;
}

.section-title {
    text-align: center;
    font-size: 24px;
    margin: 20px 0;
}

.price-list {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
}

.price-card {
    background: #141b2a;
    border: 1px solid #30394b;
    border-radius: 15px;
    padding: 15px 10px;
    text-align: center;
}

.price {
    font-size: 24px;
    font-weight: bold;
    color: #ffd700;
    margin: 10px 0;
}

.gift-value {
    color: #aab3c5;
    font-size: 14px;
}

.back {
    display: block;
    text-align: center;
    color: #ffd700;
    margin: 25px 0;
    text-decoration: none;
}

.confirm {
    max-width: 450px;
    margin: 25px auto;
    background: #141b2a;
    border: 1px solid #30394b;
    border-radius: 20px;
    padding: 24px;
    text-align: center;
}

.qr {
    background: white;
    padding: 12px;
    border-radius: 15px;
    width: 240px;
    max-width: 100%;
    margin: 15px auto;
    display: block;
}

.upi {
    background: #080b12;
    border: 1px solid #30394b;
    border-radius: 10px;
    padding: 12px;
    overflow-wrap: anywhere;
    color: #ffd700;
}

.notice {
    background: #332719;
    border: 1px solid #7b5727;
    border-radius: 12px;
    padding: 13px;
    color: #ffda9b;
    font-size: 13px;
    line-height: 1.6;
    margin-top: 20px;
}

footer {
    text-align: center;
    padding: 25px 10px;
    color: #737e92;
    font-size: 13px;
}

@media (max-width: 350px) {
    .products, .price-list {
        grid-template-columns: 1fr;
    }
}
</style>
"""

HOME_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>GiftCard Store</title>
    <meta name="viewport"
          content="width=device-width, initial-scale=1">
    {{ style|safe }}
</head>
<body>

<header>🎁 GiftCard Store</header>

<div class="hero">
    <div style="font-size:45px">🎁</div>
    <h1>Gift Cards Store</h1>
    <p>
        Choose your favourite gift card<br>
        Select an amount and scan to pay.
    </p>
</div>

<div class="products">
{% for key, product in products.items() %}
    <div class="card"
         style="border-top:3px solid {{ product.color }}">
        <div class="emoji">{{ product.emoji }}</div>
        <h3>{{ product.name }}</h3>
        <p>Gift cards from ₹2,000 value</p>

        <form action="/buy/{{ key }}" method="get">
            <button type="submit">Buy Now →</button>
        </form>
    </div>
{% endfor %}
</div>

<footer>🎁 GiftCard Store | All Rights Reserved</footer>

</body>
</html>
"""

BUY_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ product.name }}</title>
    <meta name="viewport"
          content="width=device-width, initial-scale=1">
    {{ style|safe }}
</head>
<body>

<header>🎁 GiftCard Store</header>

<div class="container">

    <div class="hero">
        <div class="emoji">{{ product.emoji }}</div>
        <h1>{{ product.name }}</h1>
        <p>Select your preferred amount</p>
    </div>

    <h2 class="section-title">💰 Choose Amount</h2>

    <div class="price-list">
    {% for amount in amounts %}
        <div class="price-card">
            <div class="price">₹{{ amount }}</div>

            <div class="gift-value">
                Gift card value<br>
                <b>₹{{ amount * 4 }}</b>
            </div>

            <form action="/checkout/{{ key }}/{{ amount }}"
                  method="get">
                <button type="submit">Buy Now</button>
            </form>
        </div>
    {% endfor %}
    </div>

    <a class="back" href="/">← Back to Gift Cards</a>
</div>

<footer>🎁 GiftCard Store</footer>

</body>
</html>
"""

CHECKOUT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Scan to Pay</title>
    <meta name="viewport"
          content="width=device-width, initial-scale=1">
    {{ style|safe }}
</head>
<body>

<header>🎁 GiftCard Store</header>

<div class="container">

    <div class="confirm">

        <div class="emoji">{{ product.emoji }}</div>
        <h2>Order Summary</h2>

        <p>{{ product.name }}</p>

        <div class="price">₹{{ amount }}</div>

        <p style="color:#aab3c5">
            Gift card value: ₹{{ gift_value }}
        </p>

        <hr style="border-color:#30394b">

        <h3>📲 Scan & Pay</h3>

        <p style="color:#aab3c5">
            Scan this QR code using any UPI app.
        </p>

        <img class="qr"
             src="data:image/png;base64,{{ qr_code }}"
             alt="UPI Payment QR Code">

        <p style="color:#aab3c5">Pay to UPI ID</p>

        <div class="upi">{{ upi_id }}</div>

        <button onclick="copyUPI()">
            📋 Copy UPI ID
        </button>

        <a href="{{ upi_link }}"
           style="text-decoration:none"
           target="_blank">
            <button>Open UPI App</button>
        </a>

        <div class="notice">
            <b>Important:</b><br>
            1. Pay exactly ₹{{ amount }}.<br>
            2. Check the receiver's UPI ID before paying.<br>
            3. Save your payment screenshot or UTR number.<br>
            4. Gift card delivery is subject to payment
            verification and stock availability.
            Do not make another payment if your first
            payment is pending.
        </div>

        <a href="/buy/{{ key }}" class="back">
            ← Choose Another Amount
        </a>

        <a href="/" class="back">
            Back to Home
        </a>
    </div>

</div>

<footer>🎁 GiftCard Store</footer>

<script>
function copyUPI() {
    navigator.clipboard.writeText("{{ upi_id }}")
        .then(() => alert("UPI ID copied!"))
        .catch(() => alert("UPI ID: {{ upi_id }}"));
}
</script>

</body>
</html>
"""


def make_qr(amount, product_name):
    upi_link = (
        "upi://pay"
        "?pa=" + quote(UPI_ID)
        + "&pn=" + quote(STORE_NAME)
        + "&am=" + str(amount)
        + "&cu=INR"
        + "&tn=" + quote(product_name)
    )

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )

    qr.add_data(upi_link)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    qr_base64 = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    return qr_base64, upi_link


@app.route("/")
def home():
    return render_template_string(
        HOME_PAGE,
        products=PRODUCTS,
        style=STYLE
    )


@app.route("/buy/<key>")
def buy(key):
    product = PRODUCTS.get(key)

    if not product:
        abort(404)

    return render_template_string(
        BUY_PAGE,
        product=product,
        key=key,
        amounts=AMOUNTS,
        style=STYLE
    )


@app.route("/checkout/<key>/<int:amount>")
def checkout(key, amount):
    product = PRODUCTS.get(key)

    if not product or amount not in AMOUNTS:
        abort(404)

    qr_code, upi_link = make_qr(
        amount,
        product["name"]
    )

    return render_template_string(
        CHECKOUT_PAGE,
        product=product,
        key=key,
        amount=amount,
        gift_value=amount * 4,
        upi_id=UPI_ID,
        qr_code=qr_code,
        upi_link=upi_link,
        style=STYLE
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=False
    )
