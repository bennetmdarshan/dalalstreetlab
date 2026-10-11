"""Deterministic fictitious prices. These are never represented as BSE quotes."""
import random, datetime, json, pathlib, math
rng=random.Random(108)
end=datetime.date.today()-datetime.timedelta(days=32)
dates=[]
d=end
while len(dates)<260:
    if d.weekday()<5: dates.append(d.isoformat())
    d-=datetime.timedelta(days=1)
dates=dates[::-1]
universe=[('RELIANCE.BO','Reliance Industries','Energy',1450,'500325'),('TCS.BO','Tata Consultancy Services','Technology',3200,'532540'),('HDFCBANK.BO','HDFC Bank','Banking',900,'500180'),('INFY.BO','Infosys','Technology',1500,'500209'),('ITC.BO','ITC','Consumer staples',410,'500875'),('SUNPHARMA.BO','Sun Pharmaceutical','Healthcare',1700,'524715'),('LT.BO','Larsen & Toubro','Industrials',3300,'500510'),('TITAN.BO','Titan Company','Consumer discretionary',3100,'500114'),('BHARTIARTL.BO','Bharti Airtel','Telecom',1800,'532454'),('POWERGRID.BO','Power Grid Corporation','Utilities',290,'532898'),('MARUTI.BO','Maruti Suzuki','Automobiles',12500,'532500'),('HINDUNILVR.BO','Hindustan Unilever','Consumer staples',2300,'500696')]
market=[rng.gauss(.00025,.008) for _ in dates]
sector={s:[rng.gauss(0,.006) for _ in dates]for s in {x[2]for x in universe}}
stocks=[]
for j,(symbol,name,sec,p,code)in enumerate(universe):
    bars=[]
    for i,date in enumerate(dates):
        o=p*math.exp(rng.gauss(0,.003)); c=o*math.exp(.0004+market[i]*(.8+j*.02)+sector[sec][i]+rng.gauss(0,.007))
        hi=max(o,c)*(1+rng.uniform(.001,.011));lo=min(o,c)*(1-rng.uniform(.001,.011));p=c
        bars.append(dict(date=date,o=round(o,2),h=round(hi,2),l=round(lo,2),c=round(c,2),v=rng.randint(300000,5000000)))
    stocks.append(dict(symbol=symbol,name=name,sector=sec,code=code,bars=bars))
out=dict(version=1,id='demo-108-'+dates[-1],mode='demo',source='Deterministic synthetic fixture — NOT actual BSE prices',priceBasis='Illustrative adjusted-price units; no dividends or splits',generatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),stocks=stocks)
pathlib.Path(__file__).resolve().parents[1].joinpath('data.json').write_text(json.dumps(out,separators=(',',':')))
