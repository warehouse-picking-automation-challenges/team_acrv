#! /usr/bin/env python
# ********************************************************************
# Software License Agreement (BSD License)
#
#  Copyright (c) 2015, University of Colorado, Boulder
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions
#  are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.
#   * Neither the name of the University of Colorado Boulder
#     nor the names of its contributors may be
#     used to endorse or promote products derived
#     from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
#  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
#  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
#  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
#  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
#  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#  POSSIBILITY OF SUCH DAMAGE.
# ********************************************************************/

# Author found at: https://github.com/Jorge-C/apc_random_orders
#   Desc:   Generate random Amazon JSON order

from __future__ import division, print_function, absolute_import

import bisect
from collections import defaultdict
import random
import string

import numpy as np


_items = ['dove_beauty_bar',
          'rawlings_baseball',
          'clorox_utility_brush',
          'dr_browns_bottle_brush',
          'dasani_water_bottle',
          'easter_turtle_sippy_cup',
          'cherokee_easy_tee_shirt',
          'folgers_classic_roast_coffee',
          'crayola_24_ct',
          'peva_shower_curtain_liner',
          'barkely_hide_bones',
          'kyjen_squeakin_eggs_plush_puppies',
          'expo_dry_erase_board_eraser',
          'scotch_duct_tape',
          'jane_eyre_dvd',
          'scotch_bubble_mailer',
          'woods_extension_cord',
          'womens_knit_gloves',
          'cool_shot_glue_sticks',
          'elmers_washable_no_run_school_glue',
          'staples_index_cards',
          'laugh_out_loud_joke_book',
          'i_am_a_bunny_book',
          'kleenex_tissue_box',
          'soft_white_lightbulb',
          'kleenex_paper_towels',
          'rolodex_jumbo_pencil_cup',
          'ticonderoga_12_pencils',
          'platinum_pets_dog_bowl',
          'hanes_tube_socks',
          'creativity_chenille_stems',
          'fiskars_scissors_red',
          'cloud_b_plush_bear',
          'safety_first_outlet_plugs',
          'fitness_gear_3lb_dumbbell',
          'oral_b_toothbrush_green',
          'up_glucose_bottle',
          'command_hooks',
          'oral_b_toothbrush_red']


def _multinomial(probabilites, start=1):
    """Choose integer in [start, start + len(probabilites))
    according to `probabilites`."""
    cum_prob = np.cumsum(probabilites)
    rv = random.random()
    return start + bisect.bisect_left(cum_prob, rv)

def fill_bins_and_tote(seed=None, probabilites=None):
    """Create random order and shelve filling, following the contest
    rules.


    Rules:
    >= 2 bins will only contain one item. Both picking targets.
    >= 2 bins will contain two items. One item from each bin will be picking target.
    >= 2 bins will contain >= 3 items. One from each will be a picking target.

    There can be duplicate items. In that case, pick either, but not
    both.

    A single item will be designated to be picked. I assume every
    order has exactly the same number of objects as number of bins

    Parameters
    ==========
    seed : int
        Seed random functions for reproducible results. Defaults to
        None

    probabilites : list of floats
        Likelyhood of filling up bins with [1, 2...]  elements the
        bins that aren't determined by the contest rules. Defaults to
        [0.7, 0.2, 0.1], so that there are no bins with more than 3
        elements.

    Returns
    =======
    dict
        Can be dumped into json

    """
    random.seed(seed)
    if probabilites is None:
        # probabilites = [0.7, 0.2, 0.1]
        probabilites = [0.15, 0.2, 0.1, 0.15, 0.2, 0.1, 0.1]

    N_bins = 3*4
    bins = ['bin_{}'.format(i.upper()) for i in string.letters[:N_bins]]

    # Let's maker sure generated filling fulfills rules
    n_items = [1, 1, 2, 2, 3, 3]
    # and then fill the rest with a random number of objects. The
    # rules say that many bins will have a single item, so we actually
    # generate more single item bins
    n_items += [_multinomial(probabilites) for _ in range(N_bins - len(n_items))]
    contents = defaultdict(list)
    random.shuffle(bins)
    for bin, n_item in zip(bins, n_items):
        for _ in range(n_item):
            contents[bin].append(random.choice(_items))

    # And after filling the shelves, we just choose a random element
    # from each bin
    tote = [random.choice(_items) for bin in sorted(bins)]

    data = {}
    data["bin_contents"] = dict(contents)
    data["tote_contents"] = tote

    return data


if __name__ == '__main__':
    import argparse
    import ast
    import json


    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str,
                        help="filename to save the json order to")
    parser.add_argument("--probabilites", "-p", default=None,
                        help="Quote delimited list of probabilites. Eg"
                        " \"[0.5, 0.2, 0.2, 0.1]\". Determines the likelyhood"
                        " of filling up with [1, 2...]  elements the bins that"
                        " aren't determined by the contest rules. Defaults"
                        " to [0.7, 0.2, 0.1], so that there are no bins with"
                        " more than 3 elements.")
    parser.add_argument("--seed", "-s", default=None)

    args = parser.parse_args()


    if args.probabilites is not None:
        args.probabilites = ast.literal_eval(args.probabilites)
        if abs(sum(args.probabilites) - 1) > 1e-14:
            raise ValueError("Please make sure your probabilites add up to 1!")

    d = fill_bins_and_tote(args.seed, args.probabilites)
    with open(args.filename, 'w') as f:
        json.dump(d, f, indent=4, separators=(',', ': '), sort_keys=True)
