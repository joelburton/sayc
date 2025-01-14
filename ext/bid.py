import re

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.errors import SphinxError
from sphinx.util.docutils import SphinxRole
from sphinx.util.typing import ExtensionMetadata

bid_re = re.compile(r"^(\d|\?)(m|M|s|t|NT|[SHDC]+)(\*\*?)?$")
shape_re = re.compile(r"(\d\d?|\?)([-=])(\d\d?|\?)([-=])(\d\d?|\?)([-=])(\d\d?|\?)")


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


class AuctionRole(SphinxRole):
    """A role to show a bid."""

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:

        # To opt out of structured formatting, start with "!": "!1 of opp's suit"
        if self.text.startswith("!"):
            bid = self.text
            alert = False
            if is_opp_bid := bid.startswith("(") and bid.endswith(")"):
                bid = bid[1:-1]
            if bid.endswith("**"):
                bid = bid.removesuffix("**")
                alert = "**"
            if bid.endswith("*"):
                bid = bid.removesuffix("*")
                alert = "*"
            bid_node = nodes.inline("", bid[1:], classes=["bid"])
            if alert == "**":
                bid_node.attributes["classes"].append("bid-announce")
            if alert == "*":
                bid_node.attributes["classes"].append("bid-alert")
            if is_opp_bid:
                bid_node.attributes["classes"].append("bid-opp")
            return [nodes.inline("", "", bid_node, classes=["auction"])], []

        bid_actions_nodes = []
        for bid_action in self.text.split("-"):
            bid_alt_nodes = []

            # remember that this is an opponent bid-action, so we can ultimately put in (bid_action)
            if is_opp_bid := bid_action.startswith("(") and bid_action.endswith(")"):
                bid_action = bid_action[1:-1]

            # 1S and 1S/1H are both "bid groups" (one or more possible bids in a single action)

            for bid_alt in bid_action.split("/"):
                alert = False

                if bid_alt == "p" or bid_alt == "p*":
                    ns = [nodes.inline(text="p", classes=["bid-pass"])]
                    if bid_alt == "p*":
                        alert = "*"
                elif bid_alt == "X" or bid_alt == "X*":
                    ns = [nodes.inline(text="X", classes=["bid-x"])]
                    if bid_alt == "X*":
                        alert = "*"
                elif bid_alt == "XX" or bid_alt == "XX*":
                    ns = [nodes.inline(text="XX", classes=["bid-xx"])]
                    if bid_alt == "XX*":
                        alert = "*"
                else:
                    mo = bid_re.match(bid_alt)
                    if not mo:
                        raise SphinxError(f"Invalid bid: {self.rawtext} at {self.get_location()}")

                    level, strain_group, alert = mo.groups()
                    ns = [nodes.inline(text=level, classes=["bid-level"])]
                    if strain_group == "NT":
                        ns.append(nodes.inline(text="NT", classes=["bid-strain", "nt"]))
                    else:
                        for strain in strain_group:
                            if strain == "H":
                                strain, cls = "♥", "h"
                            elif strain == "C":
                                strain, cls = "♣", "c"
                            elif strain == "S":
                                strain, cls = "♠", "s"
                            elif strain == "D":
                                strain, cls = "♦", "d"
                            elif strain == "N":
                                strain, cls = "NT", "nt"
                            else:
                                cls = "unk"
                            ns.append(nodes.inline(text=strain, classes=["bid-strain", cls]))

                bid_alt_node = nodes.inline("", "", *ns, classes=["bid"])
                if alert == "*":
                    bid_alt_node.attributes["classes"].append("bid-alert")
                if alert == "**":
                    bid_alt_node.attributes["classes"].append("bid-announce")
                bid_alt_nodes.append(bid_alt_node)

            bid_action_node = nodes.inline(
                "", "",
                *chain_sep(*bid_alt_nodes, sep=nodes.inline(text="/", classes=["bid-alt-sep"])),
                classes=["bid-action"])
            if is_opp_bid:
                bid_action_node.attributes["classes"].append("bid-opp")
            bid_actions_nodes.append(bid_action_node)

        auction_nodes = chain_sep(*bid_actions_nodes, sep=nodes.inline(text="-", classes=["bid-sep"]))
        return [nodes.inline("", "", *auction_nodes, classes=["auction"])], []


class SuitRole(SphinxRole):
    """A role to show a suit."""

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        cls = []
        ns = []
        for c in self.text:
            if c == "(":
                cls = ["card-lead"]
            elif c == ")":
                cls = []
            else:
                ns.append(nodes.inline(text=c, classes=cls))
        return [nodes.inline("", "", *ns, classes=["suit"])], []


class HandRole(SphinxRole):
    """A role to show a hand."""

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        spades, hearts, diamonds, clubs = self.text.split(" ")
        sout = nodes.inline(
            "", "",
            nodes.inline(text="♠", classes=["s"]), nodes.Text(spades),
            classes=["hand-spades"])
        hout = nodes.inline(
            "", "",
            nodes.inline(text="♥", classes=["h"]), nodes.Text(hearts),
            classes=["hand-hearts"])
        dout = nodes.inline(
            "", "",
            nodes.inline(text="♦", classes=["d"]), nodes.Text(diamonds),
            classes=["hand-diamonds"])
        cout = nodes.inline(
            "", "",
            nodes.inline(text="♣", classes=["c"]), nodes.Text(clubs),
            classes=["hand-clubs"])
        return [nodes.inline("", "", sout, hout, dout, cout, classes=["hand"])], []


class ShapeRole(SphinxRole):
    """A role to show a hand shape."""

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        mo = shape_re.match(self.text)
        if not mo:
            raise SphinxError(f"Invalid shape: {self.rawtext} at {self.get_location()}")
        s, s1, h, s2, d, s3, c = mo.groups()
        if not s1 == s2 == s3:
            raise SphinxError(f"Invalid shape: {self.rawtext} at {self.get_location()}")
        return [
            nodes.inline(
                "", "",
                nodes.inline(text=s, classes=["shape-suit"]),
                nodes.inline(text=s1, classes=["shape-sep"]),
                nodes.inline(text=h, classes=["shape-suit"]),
                nodes.inline(text=s2, classes=["shape-sep"]),
                nodes.inline(text=d, classes=["shape-suit"]),
                nodes.inline(text=s3, classes=["shape-sep"]),
                nodes.inline(text=c, classes=["shape-suit"]),
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
