	# waveform3d

============

waveform3d converts music or audio to a 3D ".stl" file which can be printed by a 3D printer.
It is possible to either retrieve information online (through The Echo Nest services) or convert a local file stored on the hard drive.

The output can be:
  - waveform
  - pitches/timbre list
  - frequency components (i.e. audio spectrum)

## Dependencies

  - numpy
  - [librosa](https://github.com/bmcfee/librosa/)
  - [pyen](https://github.com/plamere/pyen/)
  - [stl_tools](https://github.com/thearn/stl_tools/)

# Quick Examples

Create a 3D model of the waveform of the song "No Surprises" by Radiohead:

	from waveform3d import Waveform3d
	wf = Waveform3d()

	wf.online_music_3d("Radiohead", "No surprises")

Create a 3D model of the pitches of the song "No Surprises" by Radiohead:

	wf.online_music_3d("Radiohead", "No surprises", mode="pitches")

Create a 3D model of the spectrum of the file "voice.wav" contained in the "data" folder:

	wf.local_audio_3d("data/voice.wav", mode="stft")