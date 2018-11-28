class Header(object):
    def __init__(self, seq, rwnd):
        self.seq = seq
        self.rwnd = rwnd
        

    def getHeader(self):
        return {"seq": self.seq, "rwnd": self.rwnd}