from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
import os
from datetime import datetime
import random
import tbk
from django.views.decorators.csrf import csrf_exempt

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

NORMAL_COMMERCE_CODE = "597020000541"
BASE_URL = 'http://localhost:8080'

normal_commerce_data = load_commerce_data(NORMAL_COMMERCE_CODE)
normal_commerce = tbk.commerce.Commerce(
    commerce_code=NORMAL_COMMERCE_CODE,
    key_data=normal_commerce_data['key_data'],
    cert_data=normal_commerce_data['cert_data'],
    tbk_cert_data=normal_commerce_data['tbk_cert_data'],
    environment=tbk.environments.DEVELOPMENT)
webpay_service = tbk.services.WebpayService(normal_commerce)

def index(request):
    template_name = 'base_tbk.html'
    data = {}
    return render(request,template_name,data)

def normal_index(request):
    template_name = 'normal/index.html'
    data = {}
    return render(request,template_name,data)

def normal_init_transaction(request):
    template_name = 'normal/init.html'
    data = {}
    if request.POST:
        transaction = webpay_service.init_transaction(
            amount=request.POST['amount'],
            buy_order=request.POST['buy_order'],
            return_url=BASE_URL + '/tbk/normal/return',
            final_url=BASE_URL + '/tbk/normal/final',
            session_id=request.POST['csrfmiddlewaretoken']
            )
        data = {
            'transaction': transaction
        }
        return render(request,template_name,data)
    return render(request,template_name,data)

@csrf_exempt
def normal_return_from_webpay(request):
    template_name = 'normal/success.html'
    template_name_fail = 'normal/failure.html'
    data = {}
    if request.POST:
        token = request.POST['token_ws']
        transaction = webpay_service.get_transaction_result(token)
        transaction_detail = transaction['detailOutput'][0]
        data = {
                'transaction':transaction,
                'transaction_detail':transaction_detail,
                'token':token
            }
        print(transaction_detail['responseCode'])
        if transaction_detail['responseCode'] == 0:
            return render(request,template_name,data)
        else:
            return render(request,template_name_fail,data)
    
def normal_final(request):
    template_name = 'normal/final.html'
    data = {}
    if request.POST:
        token = request.POST['token_ws']
        data = { 'token':token }
        return render(request,template_name,data)

