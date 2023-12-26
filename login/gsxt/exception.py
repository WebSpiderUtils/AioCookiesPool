class UnknownStatus(Exception):
    def __init__(self, status):
        self.status = status

    def __repr__(self):
        return repr(f'unknown status code [{self.status}] from gsxt.gov.cn')


class SectokenNotInCookies(Exception):
    def __str__(self):
        return repr('no sectoken in cookies')


class UnknownReturnWithLoginPage(Exception):
    def __str__(self):
        return repr('unknown content from login page')


