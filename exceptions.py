


class RecoverableError(Exception):
        def __init__(self,msg):
                super().__init__(msg)


class IrecoverableError(Exception):
        def __init__(self,msg):
                super().__init__(msg)




a = RecoverableError("oops")

raise a