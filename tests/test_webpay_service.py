import pytest

from tbk.services import WebpayService


@pytest.mark.parametrize(
    [
        "transaction_type",
        "details",
        "buy_order",
        "return_url",
        "final_url",
        "session_id",
    ],
    [
        (
            "TR_NORMAL_WS",
            [{"commerceCode": "1234", "amount": 1, "buyOrder": "buyorder1"}],
            "buyorder1",
            "https://google.com/r",
            "https://example.net/f",
            "session",
        ),
        (
            "TR_MALL_WS",
            [
                {"commerceCode": "1234", "amount": 1, "buyOrder": "buyorder1"},
                {"commerceCode": "43321", "amount": 240000, "buyOrder": "buyorder2"},
            ],
            "buyorder2",
            "https://example.net/r",
            "https://google.com/f",
            None,
        ),
    ],
)
def test_init_transaction(
    mock,
    default_commerce,
    soap_requestor,
    transaction_type,
    details,
    buy_order,
    return_url,
    final_url,
    session_id,
):
    expected_transaction_type = soap_requestor.get_enum_value.return_value
    expected_details = [mock.Mock() for __ in range(len(details))]
    expected_input = mock.Mock()
    soap_requestor.create_object.side_effect = expected_details + [expected_input]
    expected_calls = [mock.call("wsTransactionDetail", **detail) for detail in details]
    expected_input_kwargs = {
        "wSTransactionType": expected_transaction_type,
        "commerceId": default_commerce.commerce_code,
        "buyOrder": buy_order,
        "sessionId": session_id,
        "returnURL": return_url,
        "finalURL": final_url,
        "transactionDetails": expected_details,
    }
    expected_calls.append(mock.call("wsInitTransactionInput", **expected_input_kwargs))
    details = [
        WebpayService.TransactionDetail(
            commerce_code=detail["commerceCode"],
            amount=detail["amount"],
            buy_order=detail["buyOrder"],
        )
        for detail in details
    ]
    webpay_service = WebpayService(default_commerce, soap_requestor)

    result = webpay_service.init_transaction(
        transaction_type, details, buy_order, return_url, final_url, session_id
    )

    assert result is soap_requestor.request.return_value
    soap_requestor.request.assert_called_once_with("initTransaction", expected_input)
    soap_requestor.get_enum_value.assert_called_once_with(
        "wsTransactionType", transaction_type
    )
    soap_requestor.create_object.has_calls(expected_calls)


@pytest.mark.parametrize(["token"], [("1",), ("abc",)])
def test_get_transaction_result(default_commerce, soap_requestor, token):
    webpay_service = WebpayService(default_commerce, soap_requestor)

    result = webpay_service.get_transaction_result(token)

    assert result is soap_requestor.request.return_value
    soap_requestor.request.assert_called_once_with("getTransactionResult", token)


@pytest.mark.parametrize(["token"], [("1",), ("abc",)])
def test_acknowledge_transaction(default_commerce, soap_requestor, token):
    webpay_service = WebpayService(default_commerce, soap_requestor)

    result = webpay_service.acknowledge_transaction(token)

    assert result is soap_requestor.request.return_value
    soap_requestor.request.assert_called_once_with("acknowledgeTransaction", token)


@pytest.mark.parametrize(
    ["amount", "buy_order", "return_url", "final_url", "session_id"],
    [
        (1, "buyorder1", "https://google.com/r", "https://example.net/f", "session"),
        (10000, "buyorder2", "https://example.net/r", "https://google.com/f", None),
    ],
)
def test_init_transaction_normal(
    mock,
    default_commerce,
    soap_requestor,
    amount,
    buy_order,
    return_url,
    final_url,
    session_id,
):
    expected_transaction_type = soap_requestor.get_enum_value.return_value
    expected_detail = mock.Mock()
    expected_input = mock.Mock()
    soap_requestor.create_object.side_effect = [expected_detail, expected_input]
    expected_detail_kwargs = {
        "amount": amount,
        "commerceCode": default_commerce.commerce_code,
        "buyOrder": buy_order,
    }
    expected_input_kwargs = {
        "wSTransactionType": expected_transaction_type,
        "commerceId": default_commerce.commerce_code,
        "buyOrder": buy_order,
        "sessionId": session_id,
        "returnURL": return_url,
        "finalURL": final_url,
        "transactionDetails": [expected_detail],
    }
    webpay_service = WebpayService(default_commerce, soap_requestor)

    result = webpay_service.init_transaction_normal(
        amount, buy_order, return_url, final_url, session_id
    )

    assert result is soap_requestor.request.return_value
    soap_requestor.request.assert_called_once_with("initTransaction", expected_input)
    soap_requestor.get_enum_value.assert_called_once_with(
        "wsTransactionType", "TR_NORMAL_WS"
    )
    soap_requestor.create_object.has_calls(
        [
            mock.call("wsTransactionDetail", **expected_detail_kwargs),
            mock.call("wsInitTransactionInput", **expected_input_kwargs),
        ]
    )
