import os
import logging
from datetime import datetime
import random

import flask

import tbk
from tbk.soap.exceptions import SoapServerException, SoapRequestException

CERTIFICATES_DIR = os.path.join(os.path.dirname(__file__), "commerces")


def load_commerce_data(commerce_code):
    with open(
        os.path.join(CERTIFICATES_DIR, commerce_code, commerce_code + ".key"), "r"
    ) as file:
        key_data = file.read()
    with open(
        os.path.join(CERTIFICATES_DIR, commerce_code, commerce_code + ".crt"), "r"
    ) as file:
        cert_data = file.read()
    with open(os.path.join(CERTIFICATES_DIR, "tbk.pem"), "r") as file:
        tbk_cert_data = file.read()

    return {
        "key_data": key_data,
        "cert_data": cert_data,
        "tbk_cert_data": tbk_cert_data,
    }


app = flask.Flask(__name__)
app.secret_key = "TBKSESSION"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logging.getLogger("tbk").setLevel(logging.DEBUG)

HOST = os.getenv("HOST", "http://localhost")
PORT = os.getenv("PORT", 5000)
BASE_URL = "{host}:{port}".format(host=HOST, port=PORT)

NORMAL_COMMERCE_CODE = "597020000541"
ONECLICK_COMMERCE_CODE = "597020000593"


normal_commerce_data = load_commerce_data(NORMAL_COMMERCE_CODE)
normal_commerce = tbk.commerce.Commerce(
    commerce_code=NORMAL_COMMERCE_CODE,
    key_data=normal_commerce_data["key_data"],
    cert_data=normal_commerce_data["cert_data"],
    tbk_cert_data=normal_commerce_data["tbk_cert_data"],
    environment=tbk.environments.DEVELOPMENT,
)
webpay_service = tbk.services.WebpayService(normal_commerce)


oneclick_commerce_data = load_commerce_data(ONECLICK_COMMERCE_CODE)
oneclick_commerce = tbk.commerce.Commerce(
    commerce_code=ONECLICK_COMMERCE_CODE,
    key_data=oneclick_commerce_data["key_data"],
    cert_data=oneclick_commerce_data["cert_data"],
    tbk_cert_data=oneclick_commerce_data["tbk_cert_data"],
    environment=tbk.environments.DEVELOPMENT,
)


oneclick_service = tbk.services.OneClickPaymentService(oneclick_commerce)
oneclick_commerce_service = tbk.services.CommerceIntegrationService(oneclick_commerce)


@app.route("/")
def index():
    return flask.render_template("base.html")


@app.route("/normal/")
def normal_index():
    return flask.render_template("normal/index.html")


@app.route("/normal/init", methods=["POST"])
def normal_init_transaction():
    transaction = webpay_service.init_transaction(
        amount=flask.request.form["amount"],
        buy_order=flask.request.form["buy_order"],
        return_url=BASE_URL + "/normal/return",
        final_url=BASE_URL + "/normal/final",
        session_id=flask.request.form["session_id"],
    )
    return flask.render_template("normal/init.html", transaction=transaction)


@app.route("/normal/return", methods=["POST"])
def normal_return_from_webpay():
    token = flask.request.form["token_ws"]
    transaction = webpay_service.get_transaction_result(token)
    transaction_detail = transaction["detailOutput"][0]
    webpay_service.acknowledge_transaction(token)
    if transaction_detail["responseCode"] == 0:
        return flask.render_template(
            "normal/success.html",
            transaction=transaction,
            transaction_detail=transaction_detail,
            token=token,
        )
    else:
        return flask.render_template(
            "normal/failure.html",
            transaction=transaction,
            transaction_detail=transaction_detail,
            token=token,
        )


@app.route("/normal/final", methods=["POST"])
def normal_final():
    token = flask.request.form["token_ws"]
    return flask.render_template("normal/final.html", token=token)


# ONECLICK endpoints


@app.route("/oneclick/")
def oneclick_index():
    return flask.render_template("oneclick/index.html")


@app.route("/oneclick/init", methods=["POST"])
def oneclick_init_inscription():
    try:
        inscription = oneclick_service.init_inscription(
            username=flask.request.form["username"],
            email=flask.request.form["email"],
            response_url=BASE_URL + "/oneclick/return",
        )
    except SoapServerException as err:
        flask.flash(err.error)
        return flask.redirect("/oneclick/")
    except SoapRequestException as err:
        print(err.error, err.request)
        return flask.redirect("/oneclick/")
    return flask.render_template("oneclick/init.html", inscription=inscription)


@app.route("/oneclick/return", methods=["POST"])
def oneclick_return_from_webpay():
    token = flask.request.form["TBK_TOKEN"]
    transaction = oneclick_service.finish_inscription(token)
    buy_order = int(datetime.utcnow().strftime("%Y%m%d%H%M%S")) * 1000 + random.randint(
        1000, 9999
    )
    return flask.render_template(
        "oneclick/return.html", transaction=transaction, buy_order=buy_order
    )


@app.route("/oneclick/authorize", methods=["POST"])
def oneclick_authorize():
    buy_order = flask.request.form["buy_order"]
    tbk_user = flask.request.form["tbk_user"]
    amount = flask.request.form["amount"]
    username = flask.request.form["username"]
    transaction = oneclick_service.authorize(
        buy_order=buy_order, amount=amount, username=username, tbk_user=tbk_user
    )
    # capture_amount = int(int(amount) * 0.8)
    # capture = oneclick_commerce_service.capture(
    #     authorization_code=transaction['authorizationCode'], buy_order=buy_order, capture_amount=capture_amount)
    return flask.render_template(
        "oneclick/authorized.html",
        transaction=transaction,
        buy_order=buy_order,
        amount=amount,
    )


@app.route("/oneclick/refund", methods=["POST"])
def oneclick_refund():
    buy_order = flask.request.form["buy_order"]
    authorized_amount = int(flask.request.form["authorized_amount"])
    authorization_code = int(flask.request.form["authorization_code"])
    nullify_amount = int(flask.request.form["nullify_amount"])
    nullify = oneclick_commerce_service.nullify(
        authorization_code=authorization_code,
        authorized_amount=authorized_amount,
        buy_order=buy_order,
        nullify_amount=nullify_amount,
    )
    return flask.render_template("oneclick/refunded.html", nullify=nullify)


@app.route("/oneclick/release", methods=["POST"])
def oneclick_release():
    buy_order = flask.request.form["buy_order"]
    release = oneclick_service.code_reverse_oneclick(buyorder=buy_order)
    return flask.render_template("oneclick/released.html", release=release)
