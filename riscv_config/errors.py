class ValidationError(Exception):

    def __init__(self, message, errors):
        super().__init__(message)
        self.message = message
        self.errors = errors

    def __errPrint__(self, foo, space=' '):
        '''
            Function to petty print the error from cerberus.
        '''
        error = ''
        for key in foo.keys():
            for e in foo[key]:
                error += space + str(key) + ":"
                error += str(e)+"\n"
            error += "\n"
        error += "\n"
        return error.rstrip()

    def __str__(self):
        return self.message + "\n" + self.__errPrint__(self.errors)
