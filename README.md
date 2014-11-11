# waveform3d

waveform3d converts music or audio to a 3D STL file which can be printed by a 3D printer.
It is possible to either retrieve information online (through The Echo Nest services) or convert a local file stored on the hard drive.

![3D Waveform](3D_waveform.png?raw=true "Radiohead - No Surprises")

The output can be:
  - waveform
  - pitches/timbre list
  - frequency components (i.e. audio spectrum)

## Dependencies

  - numpy
  - [librosa](https://github.com/bmcfee/librosa/)
  - [pyen](https://github.com/plamere/pyen/)
  - [stl_tools](https://github.com/thearn/stl_tools/)

## Quick Examples

Create a 3D model of the waveform of the song "No Surprises" by Radiohead:

	from waveform3d import Waveform3d
	wf = Waveform3d()

	wf.online_music_3d("Radiohead", "No surprises")

Create a 3D model of the pitches of the song "No Surprises" by Radiohead:

	wf.online_music_3d("Radiohead", "No surprises", mode="pitches")

Create a 3D model of the spectrum of the file "voice.wav" contained in the "data" folder:

	wf.local_audio_3d("data/voice.wav", mode="stft")


## Settings

  - *en_api_key*: The Echo Nest API Key. It is possible to activate one [here](https://developer.echonest.com/account/register "Create an Echo Nest account").
  - *output_folder*: the name of the folder where the STL files will be exported
  - *height_Y*: the height of the final model along the Y axis (i.e. its depth)
  - *height_Z*: the height of the final model along the Z axis (i.e. its "vertical" height)
  - *min_absolute_value*: the minimum height on the Y axis of the waveform
  - *n_waveform_bars*: number of continous bars that will be merged. By varying this parameter it is possible to create an effect similar to the [Soundcloud waveform with "squared" bars](https://developers.soundcloud.com/assets/posts/waveform_rendering_blurred-e5dfdb680b95ea92d89611c513691d94.png)
  - *scale*: scales the height (surface)  of the resulting STL mesh. Tune to match needs (see [here](https://github.com/thearn/stl_tools))
  - *mask_val*: any element of the inputted array that is less than this value will not be included in the mesh (see [here](https://github.com/thearn/stl_tools))

## TODO

  - Implement "more three-dimensional" shapes, such as circles/squares etc
  - "Jewelry" option that will include holes in the 3D model
  - Implement the option of including text (e.g. name of the track, text of the voice recording, etc) on the 3D model

## Troubleshooting

In case of a "ValueError: zero-size array to reduction operation maximum which has no identity", try reducing the mask_val in the settings.