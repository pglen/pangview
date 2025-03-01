# ------------------------------------------------------------------------
# Text display state:

class TextState():

    def __init__(self):

        self.font = ""
        self.bold = False;  self.itbold = False;   self.italic = False
        self.ul = False; self.dul = False
        self.red = False;  self.blue = False; self.green = False
        self.bgred = False;  self.bgblue = False; self.bggreen = False
        self.strike = False; self.large = False; self.small = False; self.xsmall = False
        self.xlarge = False; self.xxlarge = False; self.center = False
        self.wrap = False; self.hidden = False; self.color =  ""; self.right = False
        self.indent = 0; self.margin = 0; self.size = 0; self.font = "";
        self.fixed = False; self.bgcolor = ""
        self.sub = False; self.sup = False; self.image = ""; self.link = ""; self.lmargin = 0
        self.fill = False; self.tab = 0

    def clear(self):
        for aa in self.__dict__:
            if aa[:2] == "__":
                continue
            if isinstance(self.__dict__[aa], bool):
                   self.__dict__[aa] = False
            elif isinstance(self.__dict__[aa], int):
                   self.__dict__[aa] = 0
            elif isinstance(self.__dict__[aa], str):
                   self.__dict__[aa] = ""
            else:
                print ("  Other", aa, type(self.__dict__[aa]))
                pass

