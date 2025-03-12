# RGB Processing (OSC processing)

## Ressources

https://www.youtube.com/watch?v=6cFRwgfXUN0&t=306s
https://www.youtube.com/watch?v=XCotRiUIWtg&t=3325s
    https://www.youtube.com/watch?v=6cFRwgfXUN0&t=306s
https://www.youtube.com/watch?v=YcRItb__GcQ&t=1883s

## Workflow 1

For broadband filters

### SubFrameSelector - Select subs

3.1 ''/pixel

- FWHM 
- Eccentricity
- Median
- Stars
- Noise to consider

### WBPP - Stack

- Drizzle: 2
- Dark master cosmetic correction
- To remove satellite trails: Light tab / Integration Parameters
    - Change the Rejection Algorithm to "Winsorized Sigma Clipping"
    - lower the "Sigma High" value to around 1.9
    - set Large Scale Pixel Rejection to "High"

### Linear phase

#### AutoStretch

**ScreenTransferFunction**
1) Autostretch in linked mode
2) Unlink
3) Autostretch

#### ImageSolver

#### Correct the light intensity (Pixinsight 1.9 only)

**SPFC**
- With your sensor and filter

#### Correct gradiant (Pixinsight 1.9 only)

**MGC**
- Find the accurate value
    - complexe structures
        - Gradient scale : 512 or 384
        - Structure separation to test between 1 to 5
    - non complexe structures
        - Gradient scale : 1024 or 2048
        - Structure separation to test between 1 to 3

#### Correct gradiant (Pixinsight < 1.9 only)

**DBE** or **AutoDBE script**

#### Correct stars distorsions

**BlurXTerminator**
- CorrectOnly

#### Sharpen stars

**BlurXTerminator**
- Evaluate PSF Diameter with **PSFImage** render script
    - Warning long process
- Configuration:
    - Sharpen stars: 0.20 (0.4)
    - Adjust star halos: -0.10 (0.3)
    - PSF Diameter pixels: value of (FWHMx + FWHMy) / 2, from the evaluation
        - Or Automatic PSF if you want to avoir PSF Image long process
    - Sharpen Nonstellar: 0.90 (0.6)

#### Find background

**FindBackground script**
- Exclude dark nebulosity if necessary 

#### Correct the color calibration 

**SPCC**
- White reference to G2V Star if no galaxy as target
- With your sensor and filter
- If necessary and if a dark region in the picture : Select dark background as region of interest

#### AutoStretch after color calibration

**ScreenTransferFunction**
1) Link
2) Autostretch

#### Remove stars

**StarXTerminator**
- Generate Star image selected
- Large overlap (slow) if lot of stars

#### Remove Noise on stars only

**NoiseXTerminator**
- Settings to test on preview
    - Denoise: 0.9
    - Detail: 0.15

### Non Linear phase

#### Statistical Stretch script

**Statistical Astro Stretching**
- Read the manual :)
- Boost to 0.15





#### Background Neutralization (Pixinsight 1.9 only)

**BN**
- If necessary and if a dark region in the picture : Select dark background as region of interest

**ScreenTransferFunction**
1) Link
2) Autostretch
3) Unlink








#### Gradient Correction (only with Pixinsight < 1.9)

**GradientCorrection**
- Select automatic convergence
- Remove structure protection for non bright nebulas (dark)

**BN**
- If necessary and if a dark region in the picture : Select dark background as region of interest



#### Stars processing

##### ArcsinhStrech

**ArcsinhStrech**
- Protect highlights
- Test stretch factor


#### Background Neutralization

**BackgroundNeutralization**
- Preview on a dark area of the starless image

#### Remove noise

**NoiseXTerminator**
- Settings to test on preview
    - Denoise: 0.9
    - Detail: 0.20


    ~(~starless*~stars)

### Non Linear phase




