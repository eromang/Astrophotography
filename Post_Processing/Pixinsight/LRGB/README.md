# LRGB Post Processing workflow 1

https://www.youtube.com/watch?v=7FtpC5fXTGA&t=1574s

## Split Channels
From the RGB masterlight extract
- Luminance channel
- Split RGB Channels

## Channel Combination

- Apply channel combination on the RGB channels
    - Apply global

## Background Extraction

- Extract background on each the combined RGB and L channels with **GraXpert**
    - Correction is "Substraction"

## Autostrech 

- Autostretch the produced combined RGB picture with ScreenTransfertFunction (STF)
- Unlink in STF
- Re-apply autostretch

## Color Calibration

- Apply SpectroPhotometricColorCalibration (SPCC) on RGB
    - KAF-16803 or IMX571 for QE Curve
    - Select an image reference for the sky background

## Autostrech 

- Link in STF
- Autrostretch 

## Blur Exterminator

- Evaluate with PSF Image script RGB and L channels
    - (FWHMx + FWHMy) / 2 
        - 2 on RGB
        - 1.8 on L
    - Use the smallest result value on both channels
- Create preview on starts to test sharpening and halow reduction
    - avoid dark rings
    - a lot of the star color is found in the halo, take care to not halo to much

## Noise Exterminator

- Create previews on RGB and L to test noise removal
- Use the same settings on RGB and L channels

## Strech

- Auto-strech RGB with STF Auto-Strech of the STF (Command + Stretch)
    - To get details but pay attention to not increase the noise
- Apply the same stretch on the L channel (only click on the STF strech button)

## Delinearization

- Apply the STF to the HistogramTransformation
- Apply the HistogramTransformation on the selected channel
- Disable STF on the image

Same for L or RGB, depending on which channel you started

## Channel Combination

- Use ChannelCombination
- Select Color Space CIE L*a*b
- Deselect a and b in the channels
- Add the L channel to the corresponding channel in ChannelCombination
- Apply the ChannelCombination to the RGB channel

## Curves Transformation

- Use CurveTransformation

## StarXTerminator

- Create a separate layer for the object and the stars

## Curves Transformation

- Use CurveTransformation on the object

## Dark Structure Enhance

- Use the Dark Structure Enhance script if necessary

## Reintegrate Stars

https://www.rsastro.com/ReintegrateStars/PixInsight/