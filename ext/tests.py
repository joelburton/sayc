from utils import Auction
def A(auc):
    return Auction(auc).parse()

def test_simple():
    assert A("p") == [{"opp": False, "bids": [{"bid": "p"}]}]
    assert A("1C") == [{"opp": False, "bids": [{"level": '1', "strains": ["C"]}]}]
    assert A("1C-p") == [
        {"opp": False, "bids": [{"level": '1', "strains": ["C"]}]},
        {"opp": False, "bids": [{"bid": "p"}]},
    ]
    assert A("1C-2H") == [
        {"opp": False, "bids": [{"level": '1', "strains": ["C"]}]},
        {"opp": False, "bids": [{"level": '2', "strains": ["H"]}]},
    ]
    assert A("1C-X") == [
        {"opp": False, "bids": [{"level": '1', "strains": ["C"]}]},
        {"opp": False, "bids": [{"bid": "X"}]},
    ]
    assert A("1C-XX") == [
        {"opp": False, "bids": [{"level": '1', "strains": ["C"]}]},
        {"opp": False, "bids": [{"bid": "XX"}]},
    ]

def test_opp():
    assert A("1C-(p)") == [
        {"opp": False, "bids": [{"level": '1', "strains": ["C"]}]},
        {"opp": True, "bids": [{"bid": "p"}]},
    ]
    assert A("(1C)-X") == [
        {"opp": True, "bids": [{"level": '1', "strains": ["C"]}]},
        {"opp": False, "bids": [{"bid": "X"}]},
    ]

def test_alert_announce():
    assert A("1NT**") == [
        {"opp": False, "bids": [{"level": '1', "strains": ["NT"], "announce": True}]},
    ]
    assert A("1NT-2H*") == [
        {"opp": False, "bids": [{"level": '1', "strains": ["NT"]}]},
        {"opp": False, "bids": [{"level": '2', "strains": ["H"], "alert": True}]},
    ]

def test_multistrain():
    assert A("1HC") == [
        {"opp": False, "bids": [{"level": '1', "strains": ["H", "C"]}]},
    ]

def test_alt():
    assert A("1HC/2S-p") == [
        {"opp": False, "bids": [
            {"level": '1', "strains": ["H", "C"]},
            {"level": '2', "strains": ["S"]}
        ]},
        {"opp": False, "bids": [{"bid": "p"}]},
    ]

def test_text():
    assert A('"Slam"') == [
        {"opp": False, "bids": [{"text": "Slam"}]}
    ]
    assert A('"Slam"*') == [
        {"opp": False, "bids": [{"text": "Slam", "alert": True}]}
    ]
    assert A('"Slam"/1C') == [
        {"opp": False, "bids": [
            {"text": "Slam"},
            {"level": '1', "strains": ["C"]},
            ]}
    ]
    assert A('("Slam")-p') == [
        {"opp": True, "bids": [{"text": "Slam"}]},
        {"opp": False, "bids": [{"bid": "p"}]},
    ]

def test_lead_trail():
    assert A("-p") == [
        None,
        {"opp": False, "bids": [{"bid": "p"}]},
    ]
    assert A("p-") == [
        {"opp": False, "bids": [{"bid": "p"}]},
        None,
    ]
