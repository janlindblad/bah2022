#!/usr/bin/env python3

import pandas, sys, math
import matplotlib.pyplot as plt

class BAH_Loader:
  def __init__(self):
    alla = 'Alla'
    ind = 'Industri (energi + processer)'
    self.rus_co2_raw = pandas.read_excel("Lansrapport_alla_CO2.xlsx", header=4, index_col=[0,1,2,3])
    self.rus_ghg_raw = pandas.read_excel("Lansrapport_alla_vaxthusgaser_totalt.xlsx", header=5, index_col=[0,1,2,3])
    self.scb_pop = pandas.read_excel("be0101_folkmangdkom1950_2021.xlsx", header=5, index_col=0).dropna(axis=0, thresh=3)

out = pandas.DataFrame()
def store(title, s):
  global out
  out = pandas.concat([out,s.rename(title)], axis=1)
  print(f'{len(out.columns)}:{title}:\n{out}')

def store_df(df):
  global out
  if out.empty:
    out = df
    print(f'A1:\n{out}')
  else:
    out = pandas.concat([out,df], axis=1)
    print(f'{len(out.columns)}:\n{out}')

def round_number(val):
  return math.floor(val*100)/100

def emission_points(emission, min_value, max_value):
  maxpoints = 2
  if emission < min_value:
    return None
  emission = min(emission, max_value) # Emissions above max_value are scored 0
  x = (emission - min_value) / (max_value - min_value)
  return round_number(maxpoints - maxpoints * x)

def get_emissions_pc(emdata, popdata, years, noind=0):
  lan_level = 0 # We don't care which Län (index 0) the Kommun is in
  yeardata = [pandas.DataFrame(
                (emdata[year]['Alla']['Alla'].droplevel(0).drop('Alla') 
                -emdata[year]['Industri (energi + processer)']['Alla'].droplevel(0).drop('Alla')*noind
                ).div(popdata[year]).dropna()
              ) for year in years]
  em_pc = yeardata.pop(0)
  while yeardata:
    em_pc = em_pc.join(yeardata.pop(0))
  store_df(em_pc)
  return em_pc

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
  store('col12-avg', kavg)
  minval = kavg.min()
  kpts = kavg.apply(lambda x:emission_points(x,minval,ceiling))
  store('col12-pts', kpts.sort_values())
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
  store('pcpa-last',klast)
  store('pcpa-first',kfirst)
  store('pcpa-fact',kfact)
  store('pcpa-perc-pa',kperc_pa)
  return kperc_pa

def col34(bahl, f, years, ceiling):
  maxpoints = 3
  minpoints = -2
  def sign(df):
    return df / df.abs()
  def math_s_curve_fn(kchg):
    return 1 - kchg.abs().pow(1 / 3)*sign(kchg)
  kchg = percent_change_pa(bahl, f, years)
  store('AvgYoY% chg',kchg)
  kchg = kchg.clip(upper=ceiling)
  minval = pandas.DataFrame([kchg.min()])
  maxval = pandas.DataFrame([kchg.max()])
  print('Min/max vals')
  print(minval)
  print(maxval)
  kpts01 = ((math_s_curve_fn(kchg)                - float(math_s_curve_fn(minval)[0][0])) /
            (float(math_s_curve_fn(maxval)[0][0]) - float(math_s_curve_fn(minval)[0][0])))
  store('0-1 scores',kpts01)
  kpts = maxpoints - (maxpoints-minpoints) * kpts01 # S-curve scale -2..3 points for this category

  print('Sorted final scores',kpts.sort_values())
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

def calc(bahl,years):
  col1_pts = col12(bahl, get_co2_emissions_pc_noind, years, 6) # min score when >6t/capita
  col2_pts = col12(bahl, get_ghg_emissions_pc_noind, years, 9) # min score when >9t/capita
  col3_pts = col34(bahl, get_co2_emissions_pc, years, 2)       # min score when >+2%yoy
  col4_pts = col34(bahl, get_ghg_emissions_pc, years, 2)       # min score when >+2%yoy
  store('col1_pts', col1_pts)
  store('col2_pts', col2_pts)
  store('col3_pts', col3_pts)
  store('col4_pts', col4_pts)
  store('total_pts', col1_pts+col2_pts+col3_pts+col4_pts)

def main():
  global out
  bahl = BAH_Loader()
  years = [2015,2016,2017,2018,2019]
  calc(bahl, years)
  print(f'\n\nFinal scores:\n{out}')
  out.to_excel(f"bah results {years[0]}-{years[-1]}.xlsx")

if __name__ == "__main__":
  main()