import re

from docutils import nodes
from docutils.nodes import inline
from sphinx.application import Sphinx
from sphinx.errors import SphinxError
from sphinx.util.docutils import SphinxRole
from sphinx.util.typing import ExtensionMetadata

from utils import Auction

shape_re = re.compile(r"(\d\d?|\?)([-=])(\d\d?|\?)([-=])(\d\d?|\?)([-=])(\d\d?|\?)")

STRAIN_TEXT_AND_CLASS = {
    "H": ("♥", "h"),
    "C": ("♣", "c"),
    "S": ("♠", "s"),
    "D": ("♦", "d"),
    "NT": ("NT", "nt"),
}

class AuctionRole(SphinxRole):
    """A role to show an auction.

    Examples:

        1C-2C
        1C-(2H)-3C          (opp bids 2H)
        1C-(p)              (pass)
        1C-(X)-XX           (double, redouble)
        2C*-2D              (alert 2C)
        1NT**-2C            (announce 1NT)
        1NT-2HS             (hearts or spades)
        1NT-2C/3S           (alternate bid)
        1C-"any"-2C         (free-style text)
        1C-"any"*-2C        (...with alert)
        1C-2C/"slam"-3NT    (...with alternate bid)
        -2C                 (change last bid)
        2C-                 (auction continues)
    """

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        try:
            auc = Auction(self.text).parse()
        except Exception as e:
            raise SphinxError(f"Could parse auction: {self.text} err={e}")

        return [self.make_auction_node(auc)], []

    def make_auction_node(self, auc):
        """Create and return auction node."""
        auc_n = inline("", "", classes=["auction"])

        for bgi, bg in enumerate(auc):
            auc_n.children.append(self.make_bid_group_node(bg))

            if bgi != len(auc) - 1:
                # Add dashes between bid groups, like in 1S-1D
                auc_n.children.append(inline(text="-", classes=["auction-bg-sep"]))

        return auc_n

    def make_bid_group_node(self, bg):
        """Make bid group node. A bid group is one bid 'action'.

            a "bid group":   1C-1NT 1C-1H/1S 1C-(1D*)
                             -- --- -- ----- -- -----
        """

        bg_n = inline("", "", classes=["bid-group"])
        if not bg:
            # Falsy bg comes from lead/trailing slash, like "-1C" or "1C-"
            return bg_n

        bids = bg["bids"]

        for bidi, bid in enumerate(bids):
            bid_n = self.make_bid_node(bid)
            bg_n.children.append(bid_n)

            if bidi != len(bids) - 1:
                # Add slashes between bid alts, like 1H/2S
                bg_n.append(inline(text="/", classes=["auction-bid-sep"]))

        if bg["opp"]:
            bg_n.attributes["classes"].append("auction-bg-opp")

        return bg_n

    def make_bid_node(self, bid):
        """Make single bid node.

            a "bid": 1C-1NT 1C-1H/1S 1C-(1D*)
                     -- --- -- -- -- --  ---
        """

        if bid.get("text"):
            # Like `"slam"`
            bid_n = inline("", bid["text"], classes=["auction-bid-text"])
        elif bid.get("bid"):
            # pass, X, XX
            cls = f"auction-bid-{bid['bid'].lower()}"
            bid_n = inline("", bid['bid'], classes=[cls])
        else:
            # level + strain(s), like 1H, 1HS
            bid_n = inline("", "", classes=["auction-bid"])
            bid_n.children.append(
                inline(text=bid["level"], classes=["bid-level"]))
            for strain in bid["strains"]:
                text, cls = STRAIN_TEXT_AND_CLASS.get(strain, (strain, "unk"))
                bid_n.children.append(
                    inline(text=text, classes=["bid-strain", cls]))

        if bid.get("alert"):
            bid_n.attributes["classes"].append("auction-bid-alert")
        if bid.get("announce"):
            bid_n.attributes["classes"].append("auction-bid-announce")

        return bid_n


class SuitRole(SphinxRole):
    """A role to show a suit: `AKxx`"""

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        cls = []
        ns = []
        for c in self.text:
            if c == "(":
                cls = ["card-lead"]
            elif c == ")":
                cls = []
            else:
                ns.append(inline(text=c, classes=cls))
        return [inline("", "", *ns, classes=["suit"])], []


class HandRole(SphinxRole):
    """A role to show a hand: `AKxx xxxx Jx Txx"""

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        try:
            spades, hearts, diamonds, clubs = self.text.split(" ")
        except:
            raise SphinxError(
                f"Invalid hand: {self.rawtext} at {self.get_location()}")

        sout = inline(
            "", "",
            inline(text="♠", classes=["s"]), nodes.Text(spades),
            classes=["hand-spades"])
        hout = inline(
            "", "",
            inline(text="♥", classes=["h"]), nodes.Text(hearts),
            classes=["hand-hearts"])
        dout = inline(
            "", "",
            inline(text="♦", classes=["d"]), nodes.Text(diamonds),
            classes=["hand-diamonds"])
        cout = inline(
            "", "",
            inline(text="♣", classes=["c"]), nodes.Text(clubs),
            classes=["hand-clubs"])
        return [inline("", "", sout, hout, dout, cout, classes=["hand"])], []


class ShapeRole(SphinxRole):
    """A role to show a hand shape."""

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        mo = shape_re.match(self.text)
        if not mo:
            raise SphinxError(
                f"Invalid shape: {self.rawtext} at {self.get_location()}")
        s, s1, h, s2, d, s3, c = mo.groups()
        if not s1 == s2 == s3:
            raise SphinxError(
                f"Invalid shape: {self.rawtext} at {self.get_location()}")
        return [
            inline(
                "", "",
                inline(text=s, classes=["shape-suit"]),
                inline(text=s1, classes=["shape-sep"]),
                inline(text=h, classes=["shape-suit"]),
                inline(text=s2, classes=["shape-sep"]),
                inline(text=d, classes=["shape-suit"]),
                inline(text=s3, classes=["shape-sep"]),
                inline(text=c, classes=["shape-suit"]),
                classes=["shape"]
            )], []


def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_role('auction', AuctionRole())
    app.add_role('hand', HandRole())
    app.add_role('suit', SuitRole())
    app.add_role('shape', ShapeRole())

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
