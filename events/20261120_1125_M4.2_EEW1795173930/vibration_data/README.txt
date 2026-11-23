Camera vibration data of an earthquake, from eqcam (https://github.com/lijun99/eqcam)

event.json        the event (origin time, epicenter, depth, magnitude)
cameras.json      per camera: location, distances, video frame rate, pixel scale, view, the mount response, the
                  P and S picks, their quality, the stream delay (from S; p_late_s: how late P was picked by
                  the same measure), the predicted arrivals (Vp 5.7, Vs 3.1 km/s), the files below
<id>_motion.csv   the motion of the camera, from 5 s before the shaking to 15 s after it, in the view of the
                  shaking: video_time_s (s from the first frame of the video), utc_received (UTC of the frame as
                  received by the recorder: later than the ground motion by the stream delay), camera_across_px,
                  camera_down_px (the shift of the image, pixels of the full frame, relative to the first frame
                  of this series), roll_mrad (rotation about the image center), scale_ppm (zoom-like change)
<id>_objects.csv  if any: the motion of objects vibrating on their own, relative to the camera (px)
<id>_spectra.csv  power spectra of the camera motion (px^2/Hz, both axes summed, band-passed 0.5-12 Hz): the
                  whole series, the noise before the arrivals, the P window (P to S), the S window (3 s from S)

Caveats: the motion is the camera's, not the ground's: it is the ground motion filtered by the camera's mount
(a pole, a mast, a building: see "mount" in cameras.json, a resonance frequency, ring-down and damping) and
scaled by the zoom (pixels, not ground units). The spectra are therefore the mount's response, not ground-motion
spectra: compared with nearby seismic stations at one event (2026-11-20, M3.9, Los Angeles), their shapes and
their S/P ratios did not match, even at a station 130 m from the camera. The frame rate limits the frequencies
(up to half of it). The picks are uncertain by about 1 s or more: the camera motion has several onsets, P starts
small, and at that event the camera S-P times were 0.3-1 s shorter than the stations', and the stream delays from
the picks and from the envelopes cross-correlated with the stations differed by 0.5-1.5 s. The times are those of
the frames as received: subtract the stream delay (cameras.json, from S, when available) to compare with seismic
data; an independent clock (e.g., one burned into the video) is better. Automated and unverified.
