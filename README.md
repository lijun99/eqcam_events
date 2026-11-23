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

**Magnitudes.** An event id is set by the alert and keeps its first magnitude (e.g., `..._M4.2_...`); the
magnitude shown (index, maps) is the catalog's when `event.json` has it, and links to the event page (`url`),
where the latest magnitude and location are.

**People are blurred** in the tiles: the review that finds the effects also returns a box around every person,
and `eqcam report` blurs them; `add_event.py` refuses a run whose boxes were not applied. The boxes come from
the model's review, so a person it missed stays visible: look over the tiles of a new event before pushing.

## Add an event

```bash
# in eqcam: the survey, and optionally the vibration and arrivals (vibration.html, arrivals.html, vibration_data)
eqcam prepare --cameras videos.csv --videos <folder> --event event.json --out <runs>/<event_id>/run
eqcam review --out <runs>/<event_id>/run --backend claude
eqcam report --out <runs>/<event_id>/run --vibration

# here (Python 3, no other dependency)
python scripts/add_event.py <runs>/<event_id>/run --inputs <runs>/<event_id>
git add events index.html && git commit -m "Add <event_id>" && git push
```

`--inputs` is the folder with the run's `videos.csv`, whose `video_url` links are kept. Before publishing:

1. **The magnitude.** Look the event up in a catalog (e.g., USGS): the alert's first magnitude is often revised.
   Put the catalog's `magnitude` (and `magnitude_type`) in `event.json`, its event page in `url`, and, if the
   event id carries the alert's magnitude, a `note`; then `eqcam report` again.
2. **The people.** Look over every `cameras/<id>/tile.jpg` of the event for people the blurring missed.
3. **The pages.** Open `map.html` (and `vibration.html`, `arrivals.html`) from `events/<event_id>/`.

`--force` replaces an event already added (after a new report); `--index-only` only rebuilds `index.html`. The
script reduces local video paths to file names and refuses to publish files that still contain the home folder,
or tiles whose people boxes were not applied.

## Publish

On GitHub: Settings -> Pages -> Build and deployment -> Deploy from a branch -> `main`, folder `/ (root)`. The
site is then at `https://<user>.github.io/eqcam_events/`. `.nojekyll` makes Pages serve the files as they are.
The maps load Leaflet from unpkg and their basemaps from USGS The National Map and CARTO.
