from votes import AP, DDHQ, MergeAllResults, Edison


class Model:
    def __init__(self, ap_state, ed_dd_state, alignment):
        self.everything = []
        if ap_state:
            self.everything += [AP(ap_state, alignment)]
        if ed_dd_state:
            self.everything += [Edison(ed_dd_state)]
            self.everything += [DDHQ(ed_dd_state, alignment)]

    def merge(self):
        return MergeAllResults([e.get_all_counties() for e in self.everything])

    def merged_totals(self):
        return self.merge()['Total']

    def best_county(self, county):
        return self.merge()[county]

    def get_best_reporting(self):
        print([e.get_reporting() for e in self.everything])
        return max([e.get_reporting() for e in self.everything])
