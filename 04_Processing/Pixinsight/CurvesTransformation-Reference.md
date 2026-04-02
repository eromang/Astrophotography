---
title: "CurvesTransformation Reference"
type: processing-workflow
software: "PixInsight"
tags:
  - processing/pixinsight
---

# CurvesTransformation — Settings Reference

The most powerful editing tool in PixInsight. Used for final contrast, saturation, color balance, and luminance adjustments on non-linear (stretched) images.

> Apply after stretching (Phase 3+). Always work on non-linear data.

---

## Channel Order

Always edit in this order:

1. **Luminance (L)** — contrast and brightness
2. **Saturation (S)** — color intensity
3. **Individual channels (R, G, B)** — color balance and fine-tuning

Apply each step separately — do luminance, apply, reset, then saturation, apply, reset, then color channels.

---

## Interpolation

Use **Akima subsplines** interpolation for smoother, more natural curves.

---

## Luminance Channel

Controls overall brightness and contrast.

### S-Curve (most common)

| Grab point | Action | Effect |
|------------|--------|--------|
| Upper 1/3 | Drag **up** | Brightens nebula/highlights |
| Lower 1/4 | Drag **down** | Deepens shadows/dark lanes/space |
| Middle | Drag **up** slightly | Brings out midtones (faint nebulosity) |

> **Key rule:** Don't let the curve lose contact with the upper-right or lower-left corners — that clips data and loses information.

### Steeper curve = more contrast

- Useful for adding drama, but can make images look blocky
- Use sparingly and check for blown highlights

### Tips

- Pull down the upper-right portion slightly if brightest areas are blowing out
- Add extra grab points to control specific tonal ranges
- Test with Real-Time Preview before applying

---

## Saturation Channel

Controls color intensity across the image.

| Grab point | Action | Effect |
|------------|--------|--------|
| Upper 1/3 | Drag **up** slightly | Enriches color in brighter areas (nebula) |
| Lower 1/4 | Drag **down** slightly | Reduces saturation in dark areas (cleaner background) |

> **Keep saturation adjustments subtle** — a very shallow S-curve is usually enough. Over-saturation is a common mistake.

---

## Individual Color Channels

### Red Channel

| Grab point | Action | Effect |
|------------|--------|--------|
| Middle | Drag **up** | Enriches Ha reds in emission nebulae |
| Lower 1/4 | Drag **down** | Neutralizes red in dark space (keeps space black) |
| Upper 1/4 | Drag **up** slightly | Enhances brighter reds for depth |

### Green Channel

| Grab point | Action | Effect |
|------------|--------|--------|
| Upper 1/4 | Drag **up** | Adds yellow warmth to bright areas (red + green = yellow) |
| Lower 1/3 | Drag **down** | Removes green cast in background/shadows |
| Middle | Drag **up** slightly | Increases perceived brightness (eye is most sensitive to green) |

> **Green is key for removing green cast** — common with broadband L-Pro on emission nebula fields. Pull down the lower portion of the green curve to fix.

### Blue Channel

| Grab point | Action | Effect |
|------------|--------|--------|
| Upper 1/3 | Drag **up** | Enriches blue in reflection nebulae or OIII regions |
| Lower 1/4 | Drag **down** | Neutralizes blue in dark space, deepens reds |
| Middle | Drag **down** | Enriches overall red tones |

---

## Workflow by Target Type

### Emission Nebulae (Ha-dominant: NGC 7000, M42, Rosette)

1. **L:** S-curve for contrast. Bring up midtones to reveal faint Ha structure
2. **S:** Shallow boost in upper 1/3
3. **R:** Boost middle to enrich Ha reds. Pull down lower 1/4
4. **G:** Pull down lower 1/3 to remove green cast. Optional slight upper boost for yellow warmth
5. **B:** Pull down lower 1/4 to neutralize space

### Galaxies (M31, NGC 5746)

1. **L:** Gentle S-curve. Be careful not to blow out bright core
2. **S:** Very subtle boost
3. **R/G/B:** Minimal adjustments — broadband targets have natural colors

### Supernova Remnants (Veil, Simeis 147)

1. **L:** Strong S-curve for dramatic contrast
2. **S:** Moderate boost to bring out filament colors
3. **G:** Boost upper 1/4 for electric blue effect on OIII filaments
4. **B:** Boost upper 1/3 for blue filaments
5. **R:** Boost middle for red Ha filaments

---

## Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Over-saturation | Neon/unnatural colors | Reset S channel, use shallower curve |
| Clipped blacks | Loss of faint detail in shadows | Ensure curve touches lower-left corner |
| Clipped whites | Blown out bright regions | Pull down upper-right portion of curve |
| Green background | Green tint in space | Pull down lower 1/3 of green channel |
| Red space | Red tint in dark areas | Pull down lower 1/4 of red channel |
| Too much contrast | Blocky, harsh appearance | Flatten the S-curve, smaller adjustments |

---

## Process

1. Open **CurvesTransformation** (Process → IntensityTransformations → CurvesTransformation)
2. Select interpolation: **Akima subsplines**
3. Open **Real-Time Preview** to see changes live
4. Work one channel at a time (L → S → R → G → B)
5. Apply after each channel group (luminance first, then color)
6. Use Ctrl+Z / Ctrl+Y to compare before/after
7. If unhappy, reset and start over — this is iterative

---

## Resources

- [Mastering Curves — Sky Story](https://www.youtube.com/watch?v=vE8-P0HfHLc) — Three case studies: Cygnus Wall, Bubble Nebula, Eastern Veil
- [Curves Transformation — Hidden Light Photography](https://www.youtube.com/watch?v=wkmOPOxCEos) — Final finishing tutorial
- [Curves Transformation — SPARQ Observatory](https://www.youtube.com/watch?v=Tq6xwC7lzc4) — LRGB contrast adjustments
- Clippings: `04_Processing/Clippings/`
