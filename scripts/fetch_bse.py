#!/usr/bin/env python3
"""Fetch personal-use, adjusted BSE historical bars through open-source yfinance.
No API key. Never substitute NSE. Never fabricate missing data. Output is local:
import it into the browser rather than redistributing provider data publicly.
"""
import argparse, datetime as dt, hashlib, json, math, pathlib, sys, time
UNIVERSE=[('RELIANCE.BO','Reliance Industries','Energy','500325'),('TCS.BO','Tata Consultancy Services','Technology','532540'),('HDFCBANK.BO','HDFC Bank','Banking','500180'),('INFY.BO','Infosys','Technology','500209'),('ITC.BO','ITC','Consumer staples','500875'),('SUNPHARMA.BO','Sun Pharmaceutical','Healthcare','524715'),('LT.BO','Larsen & Toubro','Industrials','500510'),('TITAN.BO','Titan Company','Consumer discretionary','500114'),('BHARTIARTL.BO','Bharti Airtel','Telecom','532454'),('POWERGRID.BO','Power Grid Corporation','Utilities','532898'),('MARUTI.BO','Maruti Suzuki','Automobiles','532500'),('HINDUNILVR.BO','Hindustan Unilever','Consumer staples','500696')]

def normalize(frame,cutoff):
    result={}
    for index,row in frame.iterrows():
        day=index.date().isoformat()
        if day>cutoff.isoformat(): continue
        vals=[float(row[k]) for k in ['Open','High','Low','Close','Volume']]
        if not all(math.isfinite(x) for x in vals) or min(vals[:4])<=0 or vals[4]<0: continue
        o,h,l,c,v=vals
        if h<max(o,c) or l>min(o,c) or h<l: continue
        result[day]={'date':day,'o':round(o,4),'h':round(h,4),'l':round(l,4),'c':round(c,4),'v':int(v)}
    return result

def assemble(results,cutoff):
    if len(results)!=len(UNIVERSE):raise ValueError('All requested BSE stocks must succeed. Existing output is unchanged.')
    dates=sorted(set.intersection(*(set(x) for x in results.values())))
    if len(dates)<150:raise ValueError(f'Only {len(dates)} common valid sessions. Need 150 or more; no fill-forward is allowed.')
    dates=dates[-500:]
    stocks=[{'symbol':sym,'name':name,'sector':sector,'code':code,'bars':[results[sym][day] for day in dates]}for sym,name,sector,code in UNIVERSE]
    digest=hashlib.sha256(json.dumps(stocks,sort_keys=True).encode()).hexdigest()[:12]
    return {'version':1,'id':'bse-yfinance-'+digest,'mode':'historical','source':'Yahoo Finance via open-source yfinance; personal-use historical BSE data, not an official BSE feed','priceBasis':'Yahoo auto_adjust=True OHLC, INR adjusted-price units. Splits/dividends reflected in adjustment; not credited separately.','generatedAt':dt.datetime.now(dt.timezone.utc).isoformat(),'lagDays':31,'stocks':stocks}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',default='bse-history.json')
    args=parser.parse_args()
    import yfinance as yf
    cutoff=dt.datetime.now(dt.timezone.utc).date()-dt.timedelta(days=31)
    start=cutoff-dt.timedelta(days=820)
    results={}
    for symbol,_,_,_ in UNIVERSE:
        for attempt in range(3):
            try:
                ticker=yf.Ticker(symbol)
                frame=ticker.history(start=start.isoformat(),end=(cutoff+dt.timedelta(days=1)).isoformat(),interval='1d',auto_adjust=True,actions=False,raise_errors=True)
                metadata=ticker.history_metadata
                if metadata.get('currency')!='INR':raise ValueError('Currency must be INR')
                if metadata.get('exchangeName') not in ('BSE','BOM') and 'Bombay' not in str(metadata.get('fullExchangeName','')) and 'BSE' not in str(metadata.get('fullExchangeName','')):raise ValueError('Provider did not confirm BSE exchange')
                values=normalize(frame,cutoff)
                if len(values)<150:raise ValueError('Insufficient valid historical data')
                results[symbol]=values
                print(f'{symbol}: {len(values)} valid BSE sessions',flush=True)
                break
            except Exception as exc:
                if attempt==2:raise RuntimeError(f'{symbol} failed after retries: {exc}') from exc
                time.sleep(2*(attempt+1))
        time.sleep(.5)
    dataset=assemble(results,cutoff)
    output=pathlib.Path(args.output).resolve()
    output.parent.mkdir(parents=True,exist_ok=True)
    temporary=output.with_suffix('.tmp')
    temporary.write_text(json.dumps(dataset,separators=(',',':'),allow_nan=False))
    temporary.replace(output)
    print(f'Saved {len(dataset["stocks"])} stocks through {dataset["stocks"][0]["bars"][-1]["date"]} to {output}')
if __name__=='__main__':
    try:main()
    except Exception as exc:print(f'Data fetch failed: {exc}. No synthetic replacement was written.',file=sys.stderr);sys.exit(1)
