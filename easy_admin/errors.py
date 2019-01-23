class BusinessError(Exception):
    def __init__(self, code, http_code, err_info):
        """
        业务逻辑的错误
        :param code:  逻辑错误码
        :param http_code:  http状态码
        :param err_info:  文字的错误信息
        """
        super().__init__(self)
        self.code = code
        self.err_info = err_info
        self.http_code = http_code

    def __str__(self):
        return 'code: {} status code: {} err information: {}'.format(str(self.code), str(self.http_code),
                                                                     str(self.err_info))
