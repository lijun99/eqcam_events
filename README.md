# eqcam events

Rapid surveys of public and traffic camera videos after earthquakes, made with
[eqcam](https://github.com/lijun99/eqcam), published as a static site (GitHub Pages).

## Disclaimer

**Research prototype.** The findings are produced automatically and are not verified; this is not an official
earthquake product and must not be used for emergency or safety decisions. It is not affiliated with or endorsed
by the camera operators, the streaming sites, the USGS, ShakeAlert or any agency.

The stills come from camera streams that were publicly accessible at the time of the event; all rights remain with
their owners. They are published in small number, at low resolution (the 1280 x 720 tile of four frames), without
audio, with people blurred, for non-commercial research. Full-resolution frames and videos are not stored here.

Removal requests and corrections: open an issue (without personal images or details); images are removed first
and reviewed afterwards. The full text is in [about.html](about.html), linked from the index page and from every
event map. Provided as is, without warranty.

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
  cameras/<id>/                 tile.jpg (the frames before, during and after, people blurred), motion.png;
                                with --vibration, vibration.png, vibration.json, arrivals.png
  vibration.html, arrivals.html maps of the camera vibration and of the P and S arrivals (for scientific use)
  vibration_data/, .zip         the data for further analysis: per camera the motion and the spectra (CSV),
                                cameras.json (locations, mounts, picks, stream delays), event.json, README.txt
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
