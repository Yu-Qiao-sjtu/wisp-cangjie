#!/usr/bin/env python3
"""Check declared graph/SVG integrity. Does not replace rendered visual review."""
import json, math, sys
from itertools import combinations
from pathlib import Path
from xml.etree import ElementTree as ET

ORTH_TOL = 2.0      # px tolerance for axis-aligned segments of multi-point routes
DOGLEGL_GAP = 90.0  # px boundary gap below which bends must be a direct line instead

def check(graph, svg):
    errors, warnings = [], []
    def err(s): errors.append(s)
    def finite(x): return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)
    canvas=graph.get('canvas',{})
    w,h=canvas.get('width'),canvas.get('height')
    if not all(finite(v) and v>0 for v in (w,h)):
        return ['Invalid canvas dimensions'],[]
    nodes=graph.get('nodes',[]); edges=graph.get('edges',[])
    if not nodes: err('No task nodes')
    by_id={}; edge_ids=set()
    for n in nodes:
        key=n.get('id')
        if not isinstance(key,str) or not key or key in by_id:
            err('Missing/duplicate node ID'); continue
        by_id[key]=n
        vals=[n.get(k) for k in ('x','y','width','height')]
        if not all(finite(v) for v in vals) or vals[2]<=0 or vals[3]<=0:
            err(f'{key}: invalid geometry'); continue
        x,y,nw,nh=vals
        if x<0 or y<0 or x+nw>w or y+nh>h: err(f'{key}: outside canvas')
        if not n.get('label'): err(f'{key}: empty label')
    if errors: return errors,warnings
    def rect(n): return n['x'],n['y'],n['x']+n['width'],n['y']+n['height']
    for a,b in combinations(nodes,2):
        ax,ay,ar,ab=rect(a); bx,by,br,bb=rect(b)
        if min(ar,br)>max(ax,bx) and min(ab,bb)>max(ay,by):
            err(f'Overlapping nodes: {a["id"]}, {b["id"]}')
    def boundary(p,n):
        x,y,r,b=rect(n); px,py=p; t=1.5
        return ((abs(px-x)<=t or abs(px-r)<=t) and y-t<=py<=b+t) or ((abs(py-y)<=t or abs(py-b)<=t) and x-t<=px<=r+t)
    def gap(a,b):
        ax,ay,ar,ab=rect(a); bx,by,br,bb=rect(b)
        return math.hypot(max(0,max(ax,bx)-min(ar,br)),max(0,max(ay,by)-min(ab,bb)))
    def crosses(a,b,n):
        # Segment intersects the strict interior of a node rectangle.
        x,y,r,bot=rect(n); x+=.01; y+=.01; r-=.01; bot-=.01
        lo,hi=0.,1.
        for start,delta,mn,mx in ((a[0],b[0]-a[0],x,r),(a[1],b[1]-a[1],y,bot)):
            if abs(delta)<1e-12:
                if not mn<start<mx: return False
            else:
                t1,t2=sorted(((mn-start)/delta,(mx-start)/delta))
                lo=max(lo,t1); hi=min(hi,t2)
                if lo>=hi: return False
        return True
    for e in edges:
        key=e.get('id')
        if not isinstance(key,str) or not key or key in edge_ids or key in by_id:
            err('Missing/duplicate edge ID'); continue
        edge_ids.add(key)
        if e.get('source') not in by_id or e.get('target') not in by_id:
            err(f'{key}: unknown endpoint'); continue
        if e.get('kind') not in ('flow','support'): err(f'{key}: invalid kind')
        pts=e.get('points',[])
        if len(pts)<2 or not all(isinstance(p,list) and len(p)==2 and all(finite(v) for v in p) for p in pts):
            err(f'{key}: invalid points'); continue
        if any(not(0<=p[0]<=w and 0<=p[1]<=h) for p in pts): err(f'{key}: route outside canvas')
        if len(pts)>=3:
            # Multi-point routes are bus/branch lines: every segment must be
            # strictly horizontal or vertical. Slanted bus lines are the main
            # source of "歪歪扭扭" feedback.
            if any(abs(b[0]-a[0])>ORTH_TOL and abs(b[1]-a[1])>ORTH_TOL for a,b in zip(pts,pts[1:])):
                err(f'{key}: multi-point route has non-orthogonal segments; use horizontal bus + vertical drops')
            # Nodes that sit close together must be joined by one direct line,
            # not a compensating dogleg.
            g=gap(by_id[e['source']],by_id[e['target']])
            if g<=DOGLEGL_GAP:
                warnings.append(f'{key}: boundary gap {g:.0f}px <= {DOGLEGL_GAP:.0f}px; connect adjacent nodes with one direct line instead of bends')
        for p,nid in ((pts[0],e['source']),(pts[-1],e['target'])):
            if not boundary(p,by_id[nid]): warnings.append(f'{key}: endpoint is not on rectangular boundary of {nid}; inspect actual shape')
        for a,b in zip(pts,pts[1:]):
            for n in nodes:
                if n['id'] not in (e['source'],e['target']) and crosses(a,b,n): err(f'{key}: crosses node {n["id"]}')
    seen=set(); sn={}; se={}
    for el in svg.iter():
        key=el.get('id')
        if key:
            if key in seen: err(f'Duplicate SVG id: {key}')
            seen.add(key)
        for attr,items in (('data-node-id',sn),('data-edge-id',se)):
            ident=el.get(attr)
            if ident:
                if ident in items: err(f'Duplicate SVG {attr}: {ident}')
                items[ident]=el
    if set(sn)!=set(by_id): err('SVG/JSON node IDs differ')
    if set(se)!=edge_ids: err('SVG/JSON edge IDs differ')
    for e in edges:
        el=se.get(e.get('id'))
        if el is not None:
            for k in ('source','target','kind'):
                if el.get('data-'+k)!=e.get(k): err(f'{e["id"]}: SVG {k} differs')
    return list(dict.fromkeys(errors)),list(dict.fromkeys(warnings))

if __name__=='__main__':
    if len(sys.argv)!=3:
        print('Usage: check_graph.py graph.json diagram.svg'); sys.exit(2)
    try:
        errors,warnings=check(json.loads(Path(sys.argv[1]).read_text()),ET.parse(sys.argv[2]).getroot())
    except (OSError,ValueError,TypeError,KeyError,ET.ParseError) as exc:
        print('ERROR:',exc); sys.exit(1)
    for s in errors: print('ERROR:',s)
    for s in warnings: print('WARN:',s)
    print(f'{len(errors)} errors; {len(warnings)} warnings. Rendered visual review still required.')
    sys.exit(bool(errors))
