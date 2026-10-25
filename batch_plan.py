import csv,hashlib,re
from pathlib import Path
SLOTS=('labelfront_name','labelback_name','cardfront_name','cardback_name')
FIELDS=('file_name',*SLOTS,'renderstyle_template')
STYLES=('front','back','left45','right45','top','low')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build_plan(csv_path,asset_root,output_root):
    root=Path(asset_root).resolve();out=Path(output_root).resolve();jobs=[];seen=set()
    with open(csv_path,newline='',encoding='utf-8-sig') as f:
        rows=csv.DictReader(f)
        if rows.fieldnames!=list(FIELDS):raise ValueError('CSV header must exactly match the six required fields')
        for row in rows:
            name=row['file_name'].strip();style=row['renderstyle_template'].strip()
            if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',name):raise ValueError('Unsafe output name')
            if name.casefold() in seen:raise ValueError('Duplicate output name')
            if style not in STYLES:raise ValueError('Unknown render style')
            seen.add(name.casefold());files={}
            for slot in SLOTS:
                rel=Path(row[slot]);p=(root/rel).resolve()
                if rel.is_absolute() or not p.is_relative_to(root):raise ValueError('Asset path escapes root')
                if not p.is_file():raise ValueError('Missing asset '+str(rel))
                if p.suffix.lower() not in {'.png','.jpg','.jpeg'}:raise ValueError('Unsupported image type')
                files[slot]={'path':str(p),'sha256':digest(p)}
            dest=out/(name+'.png')
            if dest.exists():raise ValueError('Output already exists; use a new version directory')
            jobs.append({'name':name,'style':style,'images':files,'output':str(dest)})
    if not jobs:raise ValueError('CSV has no jobs')
    return jobs
