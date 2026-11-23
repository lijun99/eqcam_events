#!/usr/bin/env python3
"""Add an eqcam run to this repository (events/<event_id>/) and rebuild the index page.

    python scripts/add_event.py <run> [--inputs <folder with videos.csv>] [--force]
    python scripts/add_event.py --index-only

<run> is the --out folder of eqcam (with event.json, survey.json, map.html, cameras/ ...), after eqcam report,
which blurs the people in the tiles from the people_boxes of the review. Published: the map, the survey, the
event, the metrics, the review findings, and per camera the tile (people blurred) and the motion plot; with
eqcam report --vibration, the vibration and arrivals maps, their figures, and the data for further analysis
(vibration_data/ and vibration_data.zip: the camera motion and spectra, no images). Not
published: the full-resolution frames, the originals, the videos (the map links them online, from video_url) and
motion.npz. Local paths are removed. A run whose review boxed people that were not blurred is refused.
Standard library only.
"""

import argparse
import html
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENTS = os.path.join(ROOT, 'events')
TOP_FILES = ('map.html', 'map.png', 'survey.csv', 'survey.json', 'event.json', 'metrics.json', 'tasks.json',
             'vibration.html', 'vibration_summary.png',          # the vibration ones if eqcam report --vibration
             'arrivals.html', 'arrivals_summary.png', 'vibration_data.zip')
TOP_DIRS = ('vibration_data',)                                   # the data for further analysis, copied whole
CAMERA_FILES = ('tile.jpg', 'motion.png', 'vibration.png', 'vibration.json', 'arrivals.png')
INPUT_FILES = ('videos.csv',)
# the notice on the maps: a header that folds it (folded at first on phones, narrow or touch screens, so that it
# does not hide the map) and the text
NOTICE = ('<style>#eqcam-notice{position:fixed;left:8px;bottom:24px;z-index:1000;'
          'max-width:min(340px,calc(100vw - 32px));background:rgba(255,255,255,.93);color:#222;padding:5px 8px;border-radius:4px;font:12px/1.4 sans-serif;'
          'box-shadow:0 1px 3px rgba(0,0,0,.3)}'
          '#eqcam-notice .nh{cursor:pointer;font-weight:bold;user-select:none}'
          '#eqcam-notice .nh::after{content:" \\25BE"}#eqcam-notice.closed .nh::after{content:" \\25B8"}'
          '#eqcam-notice.closed .nb{display:none}body.popup-open #eqcam-notice{display:none}'
          '@media (max-width:768px){#eqcam-notice{font-size:14px;bottom:8px}}</style>'
          '<div id="eqcam-notice"><div class="nh">&#9432; Research prototype</div><div class="nb">Automated, '
          'unverified findings; not an official product and not for emergency decisions. Camera images belong '
          'to their owners; people are blurred. <a href="../../about.html">About, sources and removal '
          'requests</a></div></div>'
          '<script>(function () { const n = document.getElementById("eqcam-notice");'
          ' n.querySelector(".nh").addEventListener("click", () => n.classList.toggle("closed"));'
          ' if (window.matchMedia("(max-width: 768px), (pointer: coarse)").matches) n.classList.add("closed"); })();'
          '</script>')
SEVERITY = {0: ('nothing notable', '#8a8f98'), 1: ('shaking effects only', '#e3b505'),
            2: ('possible damage, fire or ground failure', '#f08a24'),
            3: ('clear damage, fire or ground failure', '#d62728'), None: ('not reviewed', '#4a6fa5')}


def strip_paths(obj):
    """The video paths reduced to file names (the folders of the machine that made the run are not published)"""
    if isinstance(obj, dict):
        return {k: (os.path.basename(v) if k == 'video' and isinstance(v, str) else strip_paths(v))
                for k, v in obj.items()}
    if isinstance(obj, list):
        return [strip_paths(v) for v in obj]
    return obj


def copy_json(src, dst):
    with open(src) as f:
        data = strip_paths(json.load(f))
    with open(dst, 'w') as f:
        json.dump(data, f, indent=1)


def add_event(run, inputs=None, force=False):
    with open(os.path.join(run, 'event.json')) as f:
        event = json.load(f)
    check_masked(run)
    eid = event.get('event_id')
    if not eid or not re.fullmatch(r'[\w.-]+', eid):
        sys.exit(f'event_id {eid!r} missing or not usable as a folder name')
    dest = os.path.join(EVENTS, eid)
    if os.path.exists(dest):
        if not force:
            sys.exit(f'{dest} exists; use --force to replace it')
        shutil.rmtree(dest)
    os.makedirs(dest)
    for name in TOP_FILES:
        src = os.path.join(run, name)
        if os.path.exists(src):
            (copy_json if name.endswith('.json') else shutil.copy2)(src, os.path.join(dest, name))
    for name in INPUT_FILES:
        src = os.path.join(inputs, name) if inputs else None
        if src and os.path.exists(src):
            shutil.copy2(src, os.path.join(dest, name))
    for stage in sorted(os.listdir(os.path.join(run, 'findings'))) if os.path.isdir(os.path.join(run, 'findings')) else []:
        sdir = os.path.join(run, 'findings', stage)
        os.makedirs(os.path.join(dest, 'findings', stage), exist_ok=True)
        for name in sorted(os.listdir(sdir)):
            if name.endswith('.json'):
                copy_json(os.path.join(sdir, name), os.path.join(dest, 'findings', stage, name))
    cams = os.path.join(run, 'cameras')
    for cid in sorted(os.listdir(cams)) if os.path.isdir(cams) else []:
        for name in CAMERA_FILES:
            src = os.path.join(cams, cid, name)
            if os.path.exists(src):
                os.makedirs(os.path.join(dest, 'cameras', cid), exist_ok=True)
                shutil.copy2(src, os.path.join(dest, 'cameras', cid, name))
    for name in TOP_DIRS:
        if os.path.isdir(os.path.join(run, name)):
            shutil.copytree(os.path.join(run, name), os.path.join(dest, name))
    for page in ('map.html', 'vibration.html', 'arrivals.html'):
        add_notice(os.path.join(dest, page))
    check_no_local_paths(dest)
    print(f'added {eid} -> {os.path.relpath(dest, ROOT)}')
    return eid


def add_notice(path):
    """The notice (research prototype, unverified, rights and removal requests) on the map page"""
    if not os.path.exists(path):
        return
    with open(path) as f:
        page = f.read()
    if 'id="eqcam-notice"' not in page and '</body>' in page:
        with open(path, 'w') as f:
            f.write(page.replace('</body>', NOTICE + '</body>', 1))


def check_masked(run):
    """Refuse a run whose review boxed people that eqcam report did not blur (an older eqcam, or --no-mask)"""
    with open(os.path.join(run, 'survey.json')) as f:
        cameras = json.load(f).get('cameras', [])
    unmasked = [c['camera_id'] for c in cameras
                if (c.get('findings') or {}).get('people_boxes') and not c.get('people_blurred')]
    if unmasked:
        sys.exit(f'people not blurred in {", ".join(unmasked)}: run eqcam report (without --no-mask) first')
    unboxed = [c['camera_id'] for c in cameras if ((c.get('findings') or {}).get('people_response') or {})
               .get('present') == 'yes' and not (c.get('findings') or {}).get('people_boxes')]
    if unboxed:
        print(f'warning: people responding but no people_boxes in {", ".join(unboxed)}: check their tiles')


def check_no_local_paths(dest):
    home = os.path.expanduser('~')
    for folder, _, files in os.walk(dest):
        for name in files:
            if name.endswith(('.json', '.html', '.csv')):
                with open(os.path.join(folder, name), errors='ignore') as f:
                    if home in f.read():
                        sys.exit(f'{os.path.join(folder, name)} still contains a local path ({home}); not published')


def summary(eid):
    folder = os.path.join(EVENTS, eid)
    with open(os.path.join(folder, 'event.json')) as f:
        event = json.load(f)
    cameras = []
    if os.path.exists(os.path.join(folder, 'survey.json')):
        with open(os.path.join(folder, 'survey.json')) as f:
            cameras = json.load(f).get('cameras', [])
    counts = {}
    for c in cameras:
        counts[c.get('severity')] = counts.get(c.get('severity'), 0) + 1
    return dict(id=eid, event=event, n=len(cameras), counts=counts)


def build_index():
    e = html.escape
    events = sorted((summary(d) for d in os.listdir(EVENTS) if os.path.exists(os.path.join(EVENTS, d, 'event.json'))),
                    key=lambda s: s['event'].get('origin_utc') or s['id'], reverse=True) if os.path.isdir(EVENTS) else []
    rows = []
    for s in events:
        ev = s['event']
        when = (ev.get('origin_utc') or '').replace('T', ' ').rstrip('Z')[:19]
        badges = ''.join(f'<span class="b" style="--c:{SEVERITY[k][1]}" title="{e(SEVERITY[k][0])}">{v}</span>'
                         for k, v in sorted(s['counts'].items(), key=lambda kv: -1 if kv[0] is None else kv[0]))
        mag = ev.get('magnitude')
        mag = f'M{mag:.1f}' if isinstance(mag, (int, float)) else ''
        if mag and ev.get('url'):                          # the event page: the latest magnitude and location
            mag = f'<a href="{e(ev["url"])}" title="event page">{mag}</a>'
        rows.append(f'<tr><td>{e(when)} UTC</td><td class="m">{mag}</td>'
                    f'<td>{e(ev.get("place") or "")}<div class="id">{e(s["id"])}</div></td><td class="n">{s["n"]}</td>'
                    f'<td>{badges}</td><td class="l"><a href="events/{e(s["id"])}/map.html">map</a> '
                    f'<a href="events/{e(s["id"])}/survey.csv">table</a></td></tr>')
    legend = ''.join(f'<span class="b" style="--c:{c}"></span>{e(name)} ' for _, (name, c) in SEVERITY.items())
    body = ''.join(rows) or '<tr><td colspan="6">No events yet.</td></tr>'
    page = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Earthquake camera surveys</title>
<style>
:root {{ --bg:#fff; --fg:#1d2330; --muted:#5f6878; --line:#e3e6eb; --link:#1a5fb4; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#14171c; --fg:#e6e9ee; --muted:#9aa3b2; --line:#2a2f37; --link:#8cb4ff; }} }}
body {{ margin:0; background:var(--bg); color:var(--fg); font:15px/1.5 system-ui, -apple-system, Segoe UI, sans-serif; }}
main {{ max-width:960px; margin:0 auto; padding:32px 16px; }}
h1 {{ font-size:24px; margin:0 0 4px; }} p {{ color:var(--muted); margin:0 0 16px; }}
a {{ color:var(--link); }} .wrap {{ overflow-x:auto; }}
table {{ border-collapse:collapse; width:100%; }} th, td {{ text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); vertical-align:top; }}
th {{ font-size:12px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); }}
td.m, td.n {{ font-variant-numeric:tabular-nums; white-space:nowrap; }} td.l a {{ margin-right:8px; }}
.id {{ font-size:12px; color:var(--muted); }}
.b {{ display:inline-block; min-width:18px; padding:0 6px; margin:0 4px 2px 0; border-radius:9px; background:var(--c);
     color:#111; font-size:12px; text-align:center; }}
.legend {{ font-size:12px; color:var(--muted); margin-top:16px; }}
footer {{ font-size:13px; color:var(--muted); margin-top:28px; padding-top:12px; border-top:1px solid var(--line); }} .legend .b {{ min-width:10px; height:10px; padding:0; vertical-align:middle; }}
</style></head><body><main>
<h1>Earthquake camera surveys</h1>
<p>Public and traffic camera videos reviewed after earthquakes with <a href="https://github.com/lijun99/eqcam">eqcam</a>:
shaking, damage, fire, ground failure and outages seen by each camera. The findings are automated and unverified.</p>
<div class="wrap"><table><thead><tr><th>Origin</th><th>Mag.</th><th>Event</th><th>Cameras</th><th>Findings</th><th></th></tr></thead>
<tbody>{body}</tbody></table></div>
<div class="legend">{legend}</div>
<footer><b>Research prototype.</b> The findings are automated and unverified; this is not an official earthquake
product and must not be used for emergency or safety decisions. Camera images belong to their owners and are shown
as a few low-resolution stills, with people blurred, for non-commercial research.
<a href="about.html">About, sources and removal requests</a></footer>
</main></body></html>
'''
    with open(os.path.join(ROOT, 'index.html'), 'w') as f:
        f.write(page)
    print(f'index.html: {len(events)} events')


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('run', nargs='?', help='the --out folder of an eqcam run')
    p.add_argument('--inputs', help='the folder with the videos.csv of the run (its video_url links are kept)')
    p.add_argument('--force', action='store_true', help='replace the event if it is already there')
    p.add_argument('--index-only', action='store_true', help='only rebuild index.html')
    a = p.parse_args()
    if not a.index_only:
        if not a.run:
            p.error('give the run folder, or --index-only')
        add_event(a.run, a.inputs, a.force)
    build_index()


if __name__ == '__main__':
    main()
