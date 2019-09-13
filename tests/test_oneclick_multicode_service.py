import pytest

from tbk.services import OneClickMulticodeService


@pytest.mark.parametrize(
    "environment, url",
    [
        (
                "DEVELOPMENT",
                "https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSOneClickMulticodeService?wsdl",
        ),
        (
                "CERTIFICATION",
                "https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSOneClickMulticodeService?wsdl",
        ),
        (
                "PRODUCTION",
                "https://webpay3g.transbank.cl/WSWebpayTransaction/cxf/WSOneClickMulticodeService?wsdl",
        ),
    ],
)
def test_wsdl_url(environment, url):
    assert url == OneClickMulticodeService.get_wsdl_url_for_environment(environment)


@pytest.mark.parametrize(
    "username, email, return_url",
    [
        ("username", "email@example.net", "https://example.net/r"),
        ("user", "email@cornershop.pe", "https://cornershopapp.com/r"),
    ],
)
def test_init_inscription(
        default_commerce, soap_requestor, username, email, return_url
):
    expected_kwargs = {"username": username, "email": email, "returnUrl": return_url}
    service = OneClickMulticodeService(default_commerce, soap_requestor)

    result = service.init_inscription(username, email, return_url)

    assert result is soap_requestor.request.return_value
    soap_requestor.create_object.assert_called_once_with(
        "wsOneClickMulticodeInitInscriptionInput", **expected_kwargs
    )
    soap_requestor.request.assert_called_once_with(
        "initInscription", soap_requestor.create_object.return_value
    )


@pytest.mark.parametrize("token", [("token",), ("asdfg",)])
def test_finish_inscription(default_commerce, soap_requestor, token):
    expected_kwargs = {"token": token}
    service = OneClickMulticodeService(default_commerce, soap_requestor)

    result = service.finish_inscription(token)

    assert result is soap_requestor.request.return_value
    soap_requestor.create_object.assert_called_once_with(
        "wsOneClickMulticodeFinishInscriptionInput", **expected_kwargs
    )
    soap_requestor.request.assert_called_once_with(
        "finishInscription", soap_requestor.create_object.return_value
    )


@pytest.mark.parametrize(
    "buy_order, tbk_user, username, raw_inputs",
    [
        (
                "12345678910111213",
                "person",
                "username@example.net",
                [
                    {
                        "commerceId": "1111111",
                        "buyOrder": "12345678910111213",
                        "amount": 10000,
                        "sharesNumber": 1,
                    }
                ],
        ),
        (
                "12345678910111213",
                "person",
                "username@example.net",
                [
                    {
                        "commerceId": "1111111",
                        "buyOrder": "12345678910111213",
                        "amount": 10000,
                        "sharesNumber": 1,
                    },
                    {
                        "commerceId": "1111111222222",
                        "buyOrder": "12345678910111213",
                        "amount": "10000",
                        "sharesNumber": 0,
                    },
                ],
        ),
    ],
)
def test_authorize(
        mock, default_commerce, soap_requestor, buy_order, tbk_user, username, raw_inputs
):
    stores_input = [
        OneClickMulticodeService.StoreInput(
            commerce_id=store_input["commerceId"],
            buy_order=store_input["buyOrder"],
            amount=store_input["amount"],
            shares_number=store_input["sharesNumber"],
        )
        for store_input in raw_inputs
    ]
    expected_kwargs = {
        "username": username,
        "tbkUser": tbk_user,
        "buyOrder": buy_order,
        "storesInput": [
            {
                "buyOrder": store_input["buyOrder"],
                "sharesNumber": store_input["sharesNumber"],
                "amount": store_input["amount"],
                "commerceId": store_input["commerceId"],
            }
            for store_input in raw_inputs
        ],
    }

    service = OneClickMulticodeService(default_commerce, soap_requestor)

    result = service.authorize(buy_order, tbk_user, username, stores_input)
    assert result is soap_requestor.request.return_value
    soap_requestor.create_object.assert_called_once_with(
        "wsOneClickMulticodePaymentInput", **expected_kwargs
    )
    soap_requestor.request.assert_called_once_with(
        "authorize", soap_requestor.create_object.return_value
    )


@pytest.mark.parametrize("buy_order", [("123",), ("12345678910111213",)])
def test_reverse(default_commerce, soap_requestor, buy_order):
    expected_kwargs = {"buyOrder": buy_order}
    service = OneClickMulticodeService(default_commerce, soap_requestor)

    result = service.reverse(buy_order)

    assert result is soap_requestor.request.return_value
    soap_requestor.create_object.assert_called_once_with(
        "wsOneClickMulticodeReverseInput", **expected_kwargs
    )
    soap_requestor.request.assert_called_once_with(
        "reverse", soap_requestor.create_object.return_value
    )


@pytest.mark.parametrize(
    "commerce_id, buy_order, authorized_amount, authorization_code, nullify_amount",
    [
        ("commerce_id", "123456", "10000", "123456", "9000"),
        ("1111111111", "12345678901011", 10000, "123456", 9000),
    ],
)
def test_nullify(
        default_commerce,
        soap_requestor,
        commerce_id,
        buy_order,
        authorized_amount,
        authorization_code,
        nullify_amount,
):
    expected_kwargs = {"commerceId": commerce_id, "buyOrder": buy_order, "authorizedAmount": authorized_amount,
                       "authorizationCode": authorization_code, "nullifyAmount": nullify_amount}
    service = OneClickMulticodeService(default_commerce, soap_requestor)

    result = service.nullify(
        commerce_id, buy_order, authorization_code, authorized_amount, nullify_amount
    )

    assert result is soap_requestor.request.return_value
    assert result is soap_requestor.request.return_value
    soap_requestor.create_object.assert_called_once_with(
        "wsOneClickMulticodeNullificationInput", **expected_kwargs
    )
    soap_requestor.request.assert_called_once_with(
        "nullify", soap_requestor.create_object.return_value
    )


@pytest.mark.parametrize(
    "buy_order, commerce_id, nullify_amount",
    [("123456", "1222222", "9000"), ("1234567890", "1222313131312", 11000)],
)
def test_reverse_nullification(
        default_commerce, soap_requestor, buy_order, commerce_id, nullify_amount
):
    service = OneClickMulticodeService(default_commerce, soap_requestor)

    result = service.reverse_nullification(buy_order, nullify_amount, commerce_id)

    assert result is soap_requestor.request.return_value
    soap_requestor.create_object.assert_called_once_with(
        "wsOneClickMulticodeReverseNullificationInput",
        buyOrder=buy_order,
        commerceId=commerce_id,
        nullifyAmount=nullify_amount,
    )
    soap_requestor.request.assert_called_once_with(
        "reverseNullification", soap_requestor.create_object.return_value
    )


@pytest.mark.parametrize(
    ["tbk_user", "username"],
    [("person", "person@example.net"), ("person@example.net", "person")],
)
def test_remove_inscription(default_commerce, soap_requestor, tbk_user, username):
    oneclick_service = OneClickMulticodeService(default_commerce, soap_requestor)

    result = oneclick_service.remove_user(tbk_user, username)

    assert result is soap_requestor.request.return_value
    soap_requestor.create_object.assert_called_once_with(
        "wsOneClickMulticodeRemoveInscriptionInput", tbkUser=tbk_user, username=username
    )
    soap_requestor.request.assert_called_once_with(
        "removeInscription", soap_requestor.create_object.return_value
    )


@pytest.mark.parametrize(
    "authorization_code, buy_order, commerce_id, captured_amount",
    [
        ("123456", "1234567890101112", "123456", "9000"),
        ("654321", "123456789098765432", "12345611111", 19000),
    ],
)
def test_capture(
        default_commerce,
        soap_requestor,
        authorization_code,
        buy_order,
        commerce_id,
        captured_amount,
):
    oneclick_service = OneClickMulticodeService(default_commerce, soap_requestor)

    result = oneclick_service.capture(
        authorization_code, commerce_id, buy_order, captured_amount
    )

    assert result is soap_requestor.request.return_value
    soap_requestor.create_object.assert_called_once_with(
        "wsOneClickMulticodeCaptureInput",
        authorizationCode=authorization_code,
        buyOrder=buy_order,
        commerceId=commerce_id,
        captureAmount=captured_amount,
    )
    soap_requestor.request.assert_called_once_with(
        "capture", soap_requestor.create_object.return_value
    )
