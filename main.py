import argparse,json
from batch_plan import build_plan
p=argparse.ArgumentParser();p.add_argument('csv');p.add_argument('--assets',required=True);p.add_argument('--out',required=True);a=p.parse_args()
print(json.dumps(build_plan(a.csv,a.assets,a.out),indent=2))
