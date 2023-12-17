class UnknownStatus(Exception):
    def __init__(self, status):
        self.status = status

    def __repr__(self):
        return repr(f'unknown status code [{self.status}] from gsxt.gov.cn')
