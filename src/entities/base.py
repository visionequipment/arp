
class Base:

    def __init__(self, classtype, descr, opt_urlname=None):
        self.id = 0
        self.class_type = classtype
        self.urlname = opt_urlname.upper() if opt_urlname is not None else classtype.upper()
        self.description = descr

    def next(self):
        self.id += 1
