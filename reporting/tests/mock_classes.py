import pandas as pd


class MockMessageStatsReportsGroup:
    def __init__(self, _, group_name: str, __):
        mock_data = {
            "G1": {"data": {"delivered": [100], "delivery_prob": [0.25]}, "index": ["S1"]},
            "G2": {
                "data": {"delivered": [200, 500, 5000], "delivery_prob": [0.25, 0.30, 0.95]},
                "index": ["S2", "S3", "S4"],
            },
            "G3": {"data": {"delivered": [600], "delivery_prob": [0.9]}, "index": ["S5"]},
            "empty": {"data": {}, "index": {}},
            "error": {"data": {"foo": [1, 2, 3, 4, 5, 6, 7], "bar": [0.9]}, "index": ["S5"]},
        }
        self.df: pd.DataFrame = pd.DataFrame(data=mock_data[group_name]["data"], index=mock_data[group_name]["index"])
        self.name: str = group_name
        self.empty: bool = True if group_name == "empty" else False

    def __str__(self):
        return f"<MockReportsGroup: name={self.name}>"
