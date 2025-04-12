# ------------------------------------------------------------------------
# Text display state:

class TextState():

    def __init__(self):

        self.org = {}
        self.font = ""
        self.bold = False;  self.itbold = False;   self.italic = False
        self.ul = False; self.dul = False
        self.red = False;  self.blue = False; self.green = False
        self.bgred = False;  self.bgblue = False; self.bggreen = False
        self.strike = False; self.large = False; self.small = False; self.xsmall = False
        self.xlarge = False; self.xxlarge = False; self.center = False
        self.wrap = False; self.hidden = False; self.color =  ""; self.right = False
        self.indent = 0; self.margin = 0; self.size = 0; self.font = "";
        self.fixed = False; self.bgcolor = ""; self.left = False;
        self.sub = False; self.sup = False; self.image = ""; self.link = ""; self.lmargin = 0
        self.fill = False; self.tab = 0; self.skip = 0; self.comm2 = ""
        self.xsp = 0

        for aa in self.__dict__:
            self.org[aa] = self.__dict__[aa]

        #for aa in self.org:
        #    print(aa, self.org[aa])

    def reset(self):
        for aa in self.org:
            self.__dict__[aa] = self.org[aa]

# EOF
