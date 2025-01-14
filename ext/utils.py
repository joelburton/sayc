def chain_sep(*items, sep):
    """Chain items together with separator.

        >>> chain_sep(1, 2, 3, sep="-")
        [1, '-', 2, '-', 3]
    """

    out = []
    for i, v in enumerate(items):
        out.append(v)
        if i < len(items) - 1:
            out.append(sep)
    return out

# [  None (for start/end -) or dict:
#    "opp": True,
#    "bids": [ {
#      bid: "p","X","XX", "?"
#      text: ...,
#      level: d or ?,
#      strains: [] 1 or more of ... SHDC?tMmN
#      alert: T/F
#      transfer: T/F
#    }, ... ]

class Auction:
    def __init__(self, auc):
        self.text = list(auc)
        self.auc = []

    def parse(self):
        last_is_null = False

        while self.text[0] == "-":
            self.text = self.text[1:]
            self.auc.append(None)
        while self.text[-1] == "-":
            self.text = self.text[:-1]
            last_is_null = True

        while self.text:
            self.auc.append(self.parse_bid_group())

        if last_is_null:
            self.auc.append(None)

        return self.auc

    def parse_bid_group(self):
        bg = {"opp": False, "bids": []}

        if self.text[0] == "(":
            bg["opp"] = True
            self.text.pop(0)

        while self.text and self.text[0] != "-":
            bg["bids"].append(self.parse_bid())
            if self.text and self.text[0] == "/":
                self.text.pop(0)
            if self.text and self.text[0] == ")":
                break

        if bg["opp"]:
            if self.text and self.text[0] == ")":
                self.text.pop(0)
            else:
                raise Exception("Didn't close opp")

        if self.text and self.text[0] == "-":
            self.text.pop(0)

        # raise Exception(f"Didn't close bid group: {self.auc}, {self.text}, {bg}")

        return bg

    def parse_strains(self):
        strains = []

        while self.text and self.text[0] in "SHDCMmtos?N":
            if self.text[0:2] == ["N", "T"]:
                strains.append("NT")
                self.text.pop(0)
                self.text.pop(0)
            else:
                strains.append(self.text.pop(0))

        if not strains:
            raise Exception(f"Strain expected: {self.text} {strains}")

        return strains

    def parse_bid(self):
        bid = {}

        c = self.text.pop(0)

        if c == '"':
            text = ""
            while (c := self.text.pop(0)) != '"':
                text += c
            bid["text"] = text

        else:
            if c == "p":
                bid["bid"] = "p"
            elif c == "X" and self.text and self.text[0] == "X":   # XX
                self.text.pop(0)
                bid["bid"] = "XX"
            elif c == "X":                       # X
                bid["bid"] =  "X"
            elif c in "1234567?":
                bid["level"] = c
                bid["strains"] = self.parse_strains()
            else:
                raise Exception(f"Invalid at {c}")

        if self.text[0:2] == ["*", "*"] :       # announce
            self.text.pop(0)
            self.text.pop(0)
            bid["announce"] = True
        elif self.text[0:1] == ["*"]:
            self.text.pop(0)
            bid["alert"] = True

        if not self.text or self.text[0] == "/" or self.text[0] == "-" or self.text[0] == ")":
            return bid

        raise Exception(f"Invalid bid: {bid}, {self.text}")
