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

def get_emissions_pc(emdata, popdata, years, noind=0):
  lan_level = 0 # We don't care which Län (index 0) the Kommun is in
  yeardata = [pandas.DataFrame(
                (emdata[year]['Alla']['Alla'].droplevel(0).drop('Alla') 
                -emdata[year]['Industri (energi + processer)']['Alla'].droplevel(0).drop('Alla')*noind
                ).div(popdata[year]).dropna()
              ) for year in years]
  em_pc_noind = yeardata.pop(0)
  while yeardata:
    em_pc_noind = em_pc_noind.join(yeardata.pop(0))
  return em_pc_noind

def get_co2_emissions_pc_noind(bahl, years):
  return get_emissions_pc(bahl.rus_co2_raw, bahl.scb_pop, years, noind=1)

def get_ghg_emissions_pc_noind(bahl, years):
  return get_emissions_pc(bahl.rus_ghg_raw, bahl.scb_pop, years, noind=1)

def get_co2_emissions_pc(bahl, years):
  return get_emissions_pc(bahl.rus_co2_raw, bahl.scb_pop, years)

def get_ghg_emissions_pc(bahl, years):
  return get_emissions_pc(bahl.rus_ghg_raw, bahl.scb_pop, years)

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

def percent_change_pa(bahl, f, years):
  ktab = f(bahl,years)
  kfirst = ktab[years[0]]       # 2015: 100
  klast = ktab[years[-1]]       # 2019:  90
  kfact = klast/kfirst          # 0.9
  numyears = years[-1]-years[0] # 4
  kfact_pa = kfact**(1/numyears)# 0.9^(1/4) = 0.974
  kperc_pa = -100*(1-kfact_pa)  # -100*0.026 = -2.6%pa
  print(klast)
  print(kfirst)
  print(kfact)
  print(kperc_pa)
  return kperc_pa

def col34(bahl, f, years, ceiling):
  maxpoints = 3
  minpoints = -2
  def sign(df):
    return df / df.abs()
  def math_s_curve_fn(kchg):
    return 1 - kchg.abs().pow(1 / 3)*sign(kchg)
  kchg = percent_change_pa(bahl, f, years)
  print('Average YoY percent changes')
  print(kchg)
  kchg = kchg.clip(upper=ceiling)
  minval = pandas.DataFrame([kchg.min()])
  maxval = pandas.DataFrame([kchg.max()])
  print('Min/max vals')
  print(minval)
  print(maxval)
  kpts01 = ((math_s_curve_fn(kchg)                - float(math_s_curve_fn(minval)[0][0])) /
            (float(math_s_curve_fn(maxval)[0][0]) - float(math_s_curve_fn(minval)[0][0])))
  print('0-1 scores')
  print(kpts01)
  kpts = maxpoints - (maxpoints-minpoints) * kpts01 # S-curve scale -2..3 points for this category

  print('Sorted final scores')
  print(kpts.sort_values())
  kpts.sort_values().plot()
  plt.show()
  print(f"{kpts.values.tolist().count(0)} municipalities with zero emission score")
  return kpts

def change_points(emission, min_value, max_value):
  maxpoints = 3
  minpoints = -2
  if emission < min_value:
    return None
  emission = min(emission, max_value)
  x = (emission - min_value) / (max_value - min_value)
  return round_number(maxpoints - maxpoints * x)

def calc(bahl):
  years = [2015,2016,2017,2018,2019]
  #years = [2014,2015,2016,2017,2018]
  col1_pts = col12(bahl, get_co2_emissions_pc_noind, years, 6)
  col2_pts = col12(bahl, get_ghg_emissions_pc_noind, years, 9)
  #col3 = percent_change_pa(bahl, get_co2_emissions_pc, years)
  col3_pts = col34(bahl, get_co2_emissions_pc, years, 2)
  col4_pts = col34(bahl, get_ghg_emissions_pc, years, 2)

def main():
  bahl = BAH_Loader()
  calc(bahl)

if __name__ == "__main__":
  main()