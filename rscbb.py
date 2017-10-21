#!/usr/bin/env python

import sys
import math

from gsp import GSP
from util import argmax_index

class rscbb:
    """Balanced bidding agent"""
    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

    def initial_bid(self, reserve):
        return self.value / 2

    def slot_info(self, t, history, reserve):
        """Compute the following for each slot, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns list of tuples [(slot_id, min_bid, max_bid)], where
        min_bid is the bid needed to tie the other-agent bid for that slot
        in the last round.  If slot_id = 0, max_bid is 2 * min_bid.
        Otherwise, it's the next highest min_bid (so bidding between min_bid
        and max_bid would result in ending up in that slot)
        """
        prev_round = history.round(t-1)
        other_bids = filter(lambda (a_id, b): a_id != self.id, prev_round.bids)

        clicks = prev_round.clicks
        def compute(s):
            (min, max) = GSP.bid_range_for_slot(s, clicks, reserve, other_bids)
            if max == None:
                max = 2 * min
            return (s, min, max)
        
        info = map(compute, range(len(clicks)))
#        sys.stdout.write("slot info: %s\n" % info)
        return info

    ############ start MY CODE HERE ####################

    def expected_utils(self, t, history, reserve):
        """
        Figure out the expected utility of bidding such that we win each
        slot, assuming that everyone else keeps their bids constant from
        the previous round.

        returns a list of utilities per slot.
        """

        # extract other bids and find rankings
        prev_round_bids = history.round(t-1).bids
        other_bids = [bid_tuple for bid_tuple in prev_round_bids if bid_tuple[0] != self.id]
        ranked_bids = sorted(other_bids, reverse=True, key=lambda x: x[1])

        # prices in GSP are the next highest bid
        prices = [bid[1] for bid in ranked_bids]
        position_effects = self.__compute_position_effects(t, len(prices))

        utilities = [position_effects[i] * (self.value - prices[i]) for i in range(len(prices))]

        # print "value: {}".format(self.value)
        # print "prices: {}".format(prices)
        # print "position effect: {}".format(position_effects)
        # print "utilites: {}".format(utilities)
   
        return utilities

    def __compute_position_effects(self, t, n_positions):
        c_1_t = round(30 * math.cos(math.pi * t / 24) + 50)
        return [c_1_t * (.75 ** (j)) for j in range(n_positions)]

    ############ end MY CODE HERE ####################

    def target_slot(self, t, history, reserve):
        """Figure out the best slot to target, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns (slot_id, min_bid, max_bid), where min_bid is the bid needed to tie
        the other-agent bid for that slot in the last round.  If slot_id = 0,
        max_bid is min_bid * 2
        """
        i =  argmax_index(self.expected_utils(t, history, reserve))
        info = self.slot_info(t, history, reserve)
        return info[i]

    def bid(self, t, history, reserve):
        # The Balanced bidding strategy (BB) is the strategy for a player j that, given
        # bids b_{-j},
        # - targets the slot s*_j which maximizes his utility, that is,
        # s*_j = argmax_s {clicks_s (v_j - t_s(j))}.
        # - chooses his bid b' for the next round so as to
        # satisfy the following equation:
        # clicks_{s*_j} (v_j - t_{s*_j}(j)) = clicks_{s*_j-1}(v_j - b')
        # (p_x is the price/click in slot x)
        # If s*_j is the top slot, bid the value v_j

        prev_round = history.round(t-1)
        (slot, min_bid, max_bid) = self.target_slot(t, history, reserve)

        ############ start MY CODE HERE ####################

        # print slot
        # print min_bid
        # print max_bid

        # NOT expecting to win, just bid value
        if min_bid > self.value:
            bid = self.value
        # NOT going for the top, do balanced bidding
        elif slot > 0: 
            # compute position effects up to slot
            pos = self.__compute_position_effects(t, slot + 1) 

            # compute "balanced bid"
            bid = self.value - (pos[slot] / pos[slot - 1]) * (self.value - min_bid)
        # going for the top (i.e. slot = 0), just bid value
        else:
            bid = self.value

        return bid

        ############ end MY CODE HERE ####################

    def __repr__(self):
        return "%s(id=%d, value=%d)" % (
            self.__class__.__name__, self.id, self.value)


