import os
import logging
from datetime import datetime
import random

import flask
import tbk

CERTIFICATES_DIR = os.path.join(os.path.dirname(__file__), 'commerces')


def load_commerce_data(commerce_code):
    with open(os.path.join(CERTIFICATES_DIR, commerce_code, commerce_code + '.key'), 'r') as file:
        key_data = file.read()
    with open(os.path.join(CERTIFICATES_DIR, commerce_code, commerce_code + '.crt'), 'r') as file:
        cert_data = file.read()
    with open(os.path.join(CERTIFICATES_DIR, 'tbk.pem'), 'r') as file:
        tbk_cert_data = file.read()

    return {
        'key_data': key_data,
        'cert_data': cert_data,
        'tbk_cert_data': tbk_cert_data
    }


app = flask.Flask(__name__)
app.secret_key = 'TBKSESSION'

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logging.getLogger("tbk").setLevel(logging.DEBUG)
logging.getLogger('suds.transport.http').setLevel(logging.DEBUG)

HOST = os.getenv('HOST', 'http://localhost')
PORT = os.getenv('PORT', '5000')
BASE_URL = '{host}:{port}'.format(host=HOST, port=PORT)

NORMAL_COMMERCE_CODE = "597020000540"
ONECLICK_COMMERCE_CODE = "597044444405"
ONECLICK_MALL_CODE = "597044444429"
ONECLICK_MALL_COMMERCE_1 = "597044444430"
ONECLICK_MALL_COMMERCE_2 = "597044444431"


normal_commerce_data = load_commerce_data(NORMAL_COMMERCE_CODE)
normal_commerce = tbk.commerce.Commerce(
    commerce_code=NORMAL_COMMERCE_CODE,
    key_data=normal_commerce_data['key_data'],
    cert_data=normal_commerce_data['cert_data'],
    tbk_cert_data=normal_commerce_data['tbk_cert_data'],
    environment=tbk.environments.DEVELOPMENT)
webpay_service = tbk.services.WebpayService(normal_commerce)


oneclick_commerce_data = load_commerce_data(ONECLICK_COMMERCE_CODE)
oneclick_commerce = tbk.commerce.Commerce(
    commerce_code=ONECLICK_COMMERCE_CODE,
    key_data=oneclick_commerce_data['key_data'],
    cert_data=oneclick_commerce_data['cert_data'],
    tbk_cert_data=oneclick_commerce_data['tbk_cert_data'],
    environment=tbk.environments.DEVELOPMENT)

oneclick_mall_commerce_data = load_commerce_data(ONECLICK_MALL_CODE)
oneclick_mall_commerce = tbk.commerce.Commerce(
    commerce_code=ONECLICK_MALL_CODE,
    key_data=oneclick_mall_commerce_data['key_data'],
    cert_data=oneclick_mall_commerce_data['cert_data'],
    tbk_cert_data=oneclick_mall_commerce_data['tbk_cert_data'],
    environment=tbk.environments.DEVELOPMENT)


oneclick_service = tbk.services.OneClickPaymentService(oneclick_commerce)
oneclick_commerce_service = tbk.services.CommerceIntegrationService(oneclick_commerce)
oneclick_mall_service = tbk.services.OneClickMulticodeService(oneclick_mall_commerce)


@app.route("/")
def index():
    return flask.render_template('base.html')


@app.route("/normal/")
def normal_index():
    return flask.render_template('normal/index.html')


@app.route("/normal/init", methods=['POST'])
def normal_init_transaction():
    transaction = webpay_service.init_transaction(
        amount=flask.request.form['amount'],
        buy_order=flask.request.form['buy_order'],
        return_url=BASE_URL + '/normal/return',
        final_url=BASE_URL + '/normal/final',
        session_id=flask.request.form['session_id']
    )
    return flask.render_template('normal/init.html', transaction=transaction)

@app.route("/normal/return", methods=['POST'])
def normal_return_from_webpay():
    token = flask.request.form['token_ws']
    transaction = webpay_service.get_transaction_result(token)
    transaction_detail = transaction['detailOutput'][0]
    webpay_service.acknowledge_transaction(token)
    if transaction_detail['responseCode'] == 0:
        return flask.render_template(
            'normal/success.html',
            transaction=transaction,
            transaction_detail=transaction_detail,
            token=token
        )
    else:
        return flask.render_template(
            'normal/failure.html',
            transaction=transaction,
            transaction_detail=transaction_detail,
            token=token
        )


@app.route("/normal/final", methods=['POST'])
def normal_final():
    token = flask.request.form['token_ws']
    return flask.render_template('normal/final.html', token=token)


# ONECLICK endpoints


@app.route("/oneclick/")
def oneclick_index():
    return flask.render_template('oneclick/index.html')


@app.route("/oneclick/init", methods=['POST'])
def oneclick_init_inscription():
    inscription = oneclick_service.init_inscription(
        username=flask.request.form['username'],
        email=flask.request.form['email'],
        response_url=BASE_URL + '/oneclick/return'
    )
    return flask.render_template('oneclick/init.html', inscription=inscription)


@app.route("/oneclick/return", methods=['POST'])
def oneclick_return_from_webpay():
    token = flask.request.form['TBK_TOKEN']
    transaction = oneclick_service.finish_inscription(token)
    buy_order = int(datetime.utcnow().strftime('%Y%m%d%H%M%S')) * 1000 + random.randint(1000, 9999)
    return flask.render_template('oneclick/return.html', transaction=transaction, buy_order=buy_order)


@app.route("/oneclick/authorize", methods=['POST'])
def oneclick_authorize():
    buy_order = flask.request.form['buy_order']
    tbk_user = flask.request.form['tbk_user']
    amount = flask.request.form['amount']
    username = flask.request.form['username']
    transaction = oneclick_service.authorize(buy_order=buy_order, amount=amount, username=username, tbk_user=tbk_user)
    # capture_amount = int(int(amount) * 0.8)
    # capture = oneclick_commerce_service.capture(
    #     authorization_code=transaction['authorizationCode'], buy_order=buy_order, capture_amount=capture_amount)
    return flask.render_template('oneclick/authorized.html',
                                 transaction=transaction, buy_order=buy_order, amount=amount)


@app.route("/oneclick/refund", methods=['POST'])
def oneclick_refund():
    buy_order = flask.request.form['buy_order']
    authorized_amount = int(flask.request.form['authorized_amount'])
    authorization_code = int(flask.request.form['authorization_code'])
    nullify_amount = int(flask.request.form['nullify_amount'])
    nullify = oneclick_commerce_service.nullify(
        authorization_code=authorization_code, authorized_amount=authorized_amount,
        buy_order=buy_order, nullify_amount=nullify_amount)
    return flask.render_template('oneclick/refunded.html',
                                 nullify=nullify)


@app.route("/oneclick/release", methods=['POST'])
def oneclick_release():
    buy_order = flask.request.form['buy_order']
    release = oneclick_service.code_reverse_oneclick(buyorder=buy_order)
    return flask.render_template('oneclick/released.html',
                                 release=release)

# ONECLICK MALL endpoints

@app.route("/mall/")
def mall_index():
    return flask.render_template('mall/index.html')


@app.route("/mall/init", methods=['POST'])
def mall_init_inscription():
    inscription = oneclick_mall_service.init_inscription(
        username=flask.request.form['username'],
        email=flask.request.form['email'],
        response_url=BASE_URL + '/mall/return'
    )
    return flask.render_template('mall/init.html', inscription=inscription)


@app.route("/mall/return", methods=['POST'])
def mall_return_from_webpay():
    token = flask.request.form['TBK_TOKEN']
    transaction = oneclick_mall_service.finish_inscription(token)
    parent_order = int(datetime.utcnow().strftime('%Y%m%d%H%M%S')) * 1000 + random.randint(1000, 9999)
    buy_order_1 = int(datetime.utcnow().strftime('%Y%m%d%H%M%S')) * 1000 + random.randint(1000, 9999)
    buy_order_2 = int(datetime.utcnow().strftime('%Y%m%d%H%M%S')) * 1000 + random.randint(1000, 9999)
    return flask.render_template(
        'mall/return.html',
        transaction=transaction,
        parent_order=parent_order,
        buy_order_1=buy_order_1,
        buy_order_2=buy_order_2)


@app.route("/mall/authorize", methods=['POST'])
def mall_authorize():
    parent_order = flask.request.form['parent_order']
    tbk_user = flask.request.form['tbk_user']
    username = flask.request.form['username']

    buy_order_1 = flask.request.form['buy_order_1']
    amount_1 = flask.request.form['amount_1']
    shares_1 = flask.request.form['shares_1']

    buy_order_2 = flask.request.form['buy_order_2']
    amount_2 = flask.request.form['amount_2']
    shares_2 = flask.request.form['shares_2']

    store_inputs = [
        {
            "buy_order": buy_order_1,
            "amount": amount_1,
            "shares": shares_1,
            "commerce_id": ONECLICK_MALL_COMMERCE_1
        },
        {
            "buy_order": buy_order_2,
            "amount": amount_2,
            "shares": shares_2,
            "commerce_id": ONECLICK_MALL_COMMERCE_2
        }
    ]

    transaction = oneclick_mall_service.authorize(
        buy_order=parent_order,
        username=username,
        tbk_user=tbk_user,
        store_inputs=store_inputs
    )
    return flask.render_template('mall/authorized.html',
                                 transaction=transaction,
                                 parent_order=parent_order,
                                 buy_order_1=buy_order_1,
                                 buy_order_2=buy_order_2,
                                 amount_1=amount_1,
                                 amount_2=amount_2,
                                 commerce_1=ONECLICK_MALL_COMMERCE_1,
                                 commerce_2=ONECLICK_MALL_COMMERCE_2)

@app.route("/mall/capture", methods=['POST'])
def mall_capture():
    commerce = flask.request.form['commerce']
    buy_order = flask.request.form['buy_order']
    capture_amount = int(flask.request.form['capture_amount'])
    authorization_code = int(flask.request.form['authorization_code'])

    capture_response = oneclick_mall_service.capture(
        authorization_code=authorization_code,
        commerce_id=commerce,
        buy_order=buy_order,
        capture_amount=capture_amount
    )

    return flask.render_template('mall/captured.html',
                                 capture=capture_response)


@app.route("/mall/nullify", methods=['POST'])
def mall_refund():
    commerce_id = flask.request.form['commerce']
    buy_order = flask.request.form['buy_order']
    authorized_amount = int(flask.request.form['authorized_amount'])
    authorization_code = int(flask.request.form['authorization_code'])
    nullify_amount = int(flask.request.form['nullify_amount'])
    nullify = oneclick_mall_service.nullify(
        commerce_id=commerce_id,
        buy_order=buy_order,
        authorization_code=authorization_code,
        authorized_amount=authorized_amount,
        nullify_amount=nullify_amount)
    return flask.render_template('mall/refunded.html',
                                 nullify=nullify)


@app.route("/mall/reverse", methods=['POST'])
def mall_release():
    buy_order = flask.request.form['buy_order']
    release = oneclick_mall_service.reverse(buy_order=buy_order)
    return flask.render_template('mall/released.html',
                                 release=release)


@app.route("/mall/reverse/nullify", methods=['POST'])
def mall_release_nullification():
    buy_order = flask.request.form['buy_order']
    nullify_amount = flask.request.form['nullify_amount']
    commerce_id = flask.request.form['commerce']
    release = oneclick_mall_service.reverse_nullification(
        buy_order=buy_order,
        nullify_amount=nullify_amount,
        commerce_id=commerce_id
    )
    return flask.render_template('mall/reverse_nullify.html',
                                 release=release)


@app.route("/mall/remove", methods=['POST'])
def mall_remove_user():
    tbk_user = flask.request.form['tbk_user']
    username = flask.request.form['username']
    remove = oneclick_mall_service.remove_user(tbk_user=tbk_user, username=username)
    return flask.render_template('mall/remove.html',
                                 remove=remove)