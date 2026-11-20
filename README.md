# eqcam events

Rapid surveys of public and traffic camera videos after earthquakes, made with
[eqcam](https://github.com/lijun99/eqcam), published as a static site (GitHub Pages).

**The findings are automated and unverified**: look at the tiles and the videos before acting on them.

## Contents

```
index.html                      the list of events (rebuilt by the script)
events/<event_id>/
  map.html, map.png             the map: cameras colored by severity, filters by tag, the tile and the video
                                links (online, at the window of the detections) in each popup
  survey.csv, survey.json       one row per camera: the motion, the findings, the video window
  event.json, videos.csv        the event and the cameras (videos.csv: video_url, where the videos are online)
  metrics.json, tasks.json      the motion measured by eqcam prepare
  findings/<stage>/<id>.json    the review of each camera
  cameras/<id>/                 tile.jpg (the frames before, during and after, people blurred), motion.png
scripts/add_event.py            adds an eqcam run and rebuilds index.html
```

The videos and the full-resolution frames are not stored here; the maps link the videos online (`video_url`).

**People are blurred** in the tiles: the review that finds the effects also returns a box around every person,
and `eqcam report` blurs them; `add_event.py` refuses a run whose boxes were not applied. The boxes come from
the model's review, so a person it missed stays visible: look over the tiles of a new event before pushing.

## Add an event

```bash
eqcam prepare ... --out runs/<event_id>     # then eqcam review and eqcam report
python scripts/add_event.py ~/tools/src/eqcam/runs/<event_id>/run --inputs ~/tools/src/eqcam/runs/<event_id>
git add events index.html && git commit -m "Add <event_id>" && git push
```

`--force` replaces an event already added; `--index-only` only rebuilds `index.html`. The script reduces local
video paths to file names and refuses to publish files that still contain the home folder.

## Publish

On GitHub: Settings -> Pages -> Build and deployment -> Deploy from a branch -> `main`, folder `/ (root)`. The
site is then at `https://<user>.github.io/eqcam_events/`. `.nojekyll` makes Pages serve the files as they are.
The maps load Leaflet from unpkg and their basemaps from USGS The National Map and CARTO.
