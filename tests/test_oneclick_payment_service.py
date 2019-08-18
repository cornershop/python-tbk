import pytest

from tbk.services import OneClickPaymentService


@pytest.mark.parametrize(
    ["username", "email", "url"],
    [
        ("person", "person@example.net", "https://example.net/"),
        ("username", "user@google.net", "https://example.net/path/to"),
        ("piter", "email@cornershopapp.com", "https://cornershopapp.com/"),
    ],
)
def test_init_inscription(default_commerce, soap_requestor, username, email, url):
    oneclick_service = OneClickPaymentService(default_commerce, soap_requestor)
    expected_kwargs = {"username": username, "email": email, "responseURL": url}

    result = oneclick_service.init_inscription(
        username=username, email=email, response_url=url
    )

    assert result is soap_requestor.request.return_value
    soap_requestor.create_object.assert_called_once_with(
        "oneClickInscriptionInput", **expected_kwargs
    )
    soap_requestor.request.assert_called_once_with(
        "initInscription", soap_requestor.create_object.return_value
    )


@pytest.mark.parametrize(["token"], [("token1",), ("qwerty",)])
def test_finish_inscription(default_commerce, soap_requestor, token):
    oneclick_service = OneClickPaymentService(default_commerce, soap_requestor)

    result = oneclick_service.finish_inscription(token)

    assert result is soap_requestor.request.return_value
    soap_requestor.create_object.assert_called_once_with(
        "oneClickFinishInscriptionInput", token=token
    )
    soap_requestor.request.assert_called_once_with(
        "finishInscription", soap_requestor.create_object.return_value
    )


@pytest.mark.parametrize(
    ["buy_order", "tbk_user", "username", "amount"],
    [
        (12345, "person", "person@example.net", "1000"),
        (234567, "username", "user@google.net", "25000"),
        (123654, "piter", "email@cornershopapp.com", "32"),
    ],
)
def test_authorize(
    default_commerce, soap_requestor, buy_order, tbk_user, username, amount
):
    oneclick_service = OneClickPaymentService(default_commerce, soap_requestor)
    expected_kwargs = {
        "buyOrder": buy_order,
        "tbkUser": tbk_user,
        "username": username,
        "amount": amount,
    }

    result = oneclick_service.authorize(buy_order, tbk_user, username, amount)

    soap_requestor.create_object.assert_called_once_with(
        "oneClickPayInput", **expected_kwargs
    )
    assert result is soap_requestor.request.return_value
    soap_requestor.request.assert_called_once_with(
        "authorize", soap_requestor.create_object.return_value
    )


@pytest.mark.parametrize(["buyorder"], [("1",), ("12345678901234567890123",)])
def test_code_reverse_oneclick(default_commerce, soap_requestor, buyorder):
    oneclick_service = OneClickPaymentService(default_commerce, soap_requestor)

    result = oneclick_service.code_reverse_oneclick(buyorder)

    soap_requestor.create_object.assert_called_once_with(
        "oneClickReverseInput", buyorder=buyorder
    )
    assert result is soap_requestor.request.return_value
    soap_requestor.request.assert_called_once_with(
        "codeReverseOneClick", soap_requestor.create_object.return_value
    )


@pytest.mark.parametrize(
    ["tbk_user", "username"],
    [("person", "person@example.net"), ("person@example.net", "person")],
)
def test_remove_user(default_commerce, soap_requestor, tbk_user, username):
    oneclick_service = OneClickPaymentService(default_commerce, soap_requestor)
    expected_kwargs = {"tbkUser": tbk_user, "username": username}

    result = oneclick_service.remove_user(tbk_user, username)

    soap_requestor.create_object.assert_called_once_with(
        "oneClickRemoveUserInput", **expected_kwargs
    )
    assert result is soap_requestor.request.return_value
    soap_requestor.request.assert_called_once_with(
        "removeUser", soap_requestor.create_object.return_value
    )
