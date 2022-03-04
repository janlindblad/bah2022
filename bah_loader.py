#!/usr/bin/env python3

import pandas

class BAH_Loader:

  def __init__(self):
    alla = 'Alla'
    ind = 'Industri (energi + processer)'
    self.rus_co2_raw = pandas.read_excel("Lansrapport_alla_CO2.xlsx", header=4, index_col=[0,1,2,3])
    self.rus_ghg_raw = pandas.read_excel("Lansrapport_alla_vaxthusgaser_totalt.xlsx", header=5, index_col=[0,1,2,3])
    self.scb_pop = pandas.read_excel("be0101_folkmangdkom1950_2021.xlsx", header=5, index_col=0).dropna(axis=0, thresh=3)

""" emission_points_fn = (emission, min_value, max_value) => {
          if (emission < min_value || emission > max_value) return null;
          let x = (emission - min_value) / (max_value - min_value);

          return this.round_number(2 - 2 * x); // Linear scale 0..2 points for this category
        },
        math_s_curve_fn = (x) => {
          return 1 - Math.pow(Math.abs(x), 1 / 3) * Math.sign(x);
        },
        percent_change_points_fn = (percentage, min_value, max_value) => {
          let x =
            (math_s_curve_fn(percentage) - math_s_curve_fn(min_value)) /
            (math_s_curve_fn(max_value) - math_s_curve_fn(min_value));
          return this.round_number(3 - 5 * x); // S-curve scale -2..3 points for this category
        };
 """
