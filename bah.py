#!/usr/bin/env python3

import pandas, sys, math
import matplotlib.pyplot as plt
from bah_loader import BAH_Loader

def round_number(val):
  return math.floor(val*100)/100

def emission_points(emission, min_value, max_value):
  maxpoints = 2
  if emission < min_value:
    return None
  emission = min(emission, max_value)
  x = (emission - min_value) / (max_value - min_value)
  return round_number(maxpoints - maxpoints * x)

def get_emissions_pc_noind(emdata, popdata, years):
  lan_level = 0 # We don't care which Län (index 0) the Kommun is in
  #>>> df=df.join((rus_co2[year]['Alla']['Alla'].droplevel(0).drop('Alla') - rus_co2[year]['Industri (energi + processer)']['Alla'].droplevel(0).drop('Alla')).div(scb[year]).dropna())
  yeardata = [pandas.DataFrame(
                (emdata[year]['Alla']['Alla'].droplevel(0).drop('Alla') 
                -emdata[year]['Industri (energi + processer)']['Alla'].droplevel(0).drop('Alla')
                ).div(popdata[year]).dropna()
              ) for year in years]
  em_pc_noind = yeardata.pop(0)
  while yeardata:
    em_pc_noind = em_pc_noind.join(yeardata.pop(0))
  return em_pc_noind

def get_co2_emissions_pc_noind(bahl, years):
  return get_emissions_pc_noind(bahl.rus_co2_raw, bahl.scb_pop, years)

def get_ghg_emissions_pc_noind(bahl, years):
  return get_emissions_pc_noind(bahl.rus_ghg_raw, bahl.scb_pop, years)

def col12(bahl, f, years, ceiling):
  ktab = f(bahl,years)
  kavg = ktab.sum(axis=1)/len(years)
  print(kavg)
  minval = kavg.min()
  kpts = kavg.apply(lambda x:emission_points(x,minval,ceiling))
  print(kpts.sort_values())
  kpts.sort_values().plot()
  plt.show()
  print(f"{kpts.values.tolist().count(0)} municipalities with zero emission score")
  return kpts

def calc(bahl):
  years = [2015,2016,2017,2018,2019]
  years = [2014,2015,2016,2017,2018]
  col1_pts = col12(bahl, get_co2_emissions_pc_noind, years, 6)
  col2_pts = col12(bahl, get_ghg_emissions_pc_noind, years, 9)

def main():
  bahl = BAH_Loader()
  calc(bahl)

if __name__ == "__main__":
  main()