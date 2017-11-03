# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class WebpayServiceException(Exception):
    def __init__(self, error, code):
        super(WebpayServiceException, self).__init__(error, code)
        self.error = error
        self.code = code
