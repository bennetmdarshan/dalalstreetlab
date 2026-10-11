import unittest, importlib.util, pathlib, datetime as dt
spec=importlib.util.spec_from_file_location('fetch_bse',pathlib.Path(__file__).parents[1]/'scripts/fetch_bse.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Index:
    def __init__(self,day):self.day=day
    def date(self):return self.day
class Frame:
    def __init__(self,rows):self.rows=rows
    def iterrows(self):return iter(self.rows)
class TestFetch(unittest.TestCase):
    def test_normalizer_filters_recent_and_invalid_rows(self):
        cutoff=dt.date(2025,1,5);valid={'Open':10,'High':12,'Low':9,'Close':11,'Volume':100}
        frame=Frame([(Index(dt.date(2025,1,1)),valid),(Index(dt.date(2025,1,7)),valid),(Index(dt.date(2025,1,2)),dict(valid,High=5)),(Index(dt.date(2025,1,3)),dict(valid,Close=float('nan')))])
        result=m.normalize(frame,cutoff);self.assertEqual(list(result),['2025-01-01']);self.assertEqual(result['2025-01-01']['c'],11)
    def test_all_stocks_required(self):
        with self.assertRaises(ValueError):m.assemble({},dt.date(2025,1,1))
    def test_alignment_is_intersection_not_forward_fill(self):
        start=dt.date(2024,1,1)
        rows={(start+dt.timedelta(days=i)).isoformat():{'date':(start+dt.timedelta(days=i)).isoformat(),'o':100,'h':110,'l':90,'c':105,'v':1000}for i in range(200)}
        results={s[0]:dict(rows)for s in m.UNIVERSE};results[m.UNIVERSE[0][0]].pop(start.isoformat())
        out=m.assemble(results,dt.date(2025,1,1));self.assertEqual(out['mode'],'historical');self.assertEqual(len(out['stocks'][0]['bars']),199);self.assertTrue(all(x['symbol'].endswith('.BO')for x in out['stocks']));self.assertNotIn(start.isoformat(),[b['date']for b in out['stocks'][1]['bars']])
if __name__=='__main__':unittest.main()
