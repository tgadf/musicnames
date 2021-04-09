class masterArtistNameCorrection:
    def __init__(self):
        self.debug = False

        ## Test
        assert self.clean("3/3") == "3-3"
        assert self.clean("...Hello") == "Hello"
        

    def directoryName(self, x):
        if x is None:
            return x
        if "..." in x:
            x = x.replace("...", "")
        if "/" in x:
            x = x.replace("/", "-")
        return x


    def realName(self, x):
        if x is None:
            return [None,-1]

        lenx = len(x)
        if len(x) < 1:
            return [x,-1]

        if x[-1] != ")":
            return [x, None]


        if lenx >=5:
            if x[-3] == "(":
                try:
                    num = int(x[-2:-1])
                    val = x[:-3].strip()
                    return [val, num]
                except:
                    return [x, None]

        if lenx >= 6:
            if x[-4] == "(":
                try:
                    num = int(x[-3:-1])
                    val = x[:-4].strip()
                    return [val, num]
                except:
                    return [x, None]

        if lenx >= 7:
            if x[-4] == "(":
                try:
                    num = int(x[-3:-1])
                    val = x[:-4].strip()
                    return [val, num]
                except:
                    return [x, None]

        return [x, None]

    
    def discConv(self, x):
        if x is None:
            return ""
        x = x.replace("/", "-")
        x = x.replace("¡", "")
        while x.startswith(".") and len(x) > 1:
            x = x[1:]
        x = x.strip()
        return x

    
    def cleanMB(self, x):
        pos = [x.rfind("(")+1, x.rfind(")")]
        if sum([p > 0 for p in pos]) != len(pos):
            return x
        parval = x[pos[0]:pos[1]]
        return x[:pos[0]-2].strip()  
        
        
    def clean(self, name, debug=False):
        if debug:
            print("              Cleaning [{0}]".format(name))
        name = self.discConv(name)
        if debug:
            print("Post DiscConv Cleaning [{0}]".format(name))
        return name