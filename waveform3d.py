import json, urllib2
import librosa
import numpy as np
import pyen
from math import ceil
from stl_tools import numpy2stl

''' Create 3D-printable models of music tracks or audio files
'''

_DEFAULT_SETTINGS_FILENAME = 'settings.json'

class Waveform3d(object):

    def __init__(self, settings_filename=None):
        """ Creates a new Waveform3d.

        Args:
            settings_filename: name of the file where 
                               the settings are stored.
        """

        if settings_filename is None:
            settings_filename = _DEFAULT_SETTINGS_FILENAME
        try:
            # Load settings
            settings_file = open(settings_filename, 'rb')
            settings = json.load(settings_file)
            settings_file.close()
            # Store settings
            self.EN_API_KEY = settings['en_api_key']
            self.OUTPUT_FOLDER = settings['output_folder']
            self.height = int(settings['height'])
            self.min_absolute_value = int(settings['min_absolute_value'])
            self.n_waveform_bars = int(settings['n_waveform_bars'])
            self.scale = float(settings['scale'])
            self.mask_val = float(settings['mask_val'])
            # Additional settings
            self.scale_factor = 0.5
            self.depth_factor = 20
        except Exception, e:
            print e


    def _get_segments(self, en, artist_name, track_name):
        # Search by artist name and track name
        response = en.get('song/search', artist=artist_name, title=track_name, bucket=['audio_summary'])
        segments = None
        if response['status']['message'] == 'Success':  # track found
            # Get waveform
            analysis_url = response['songs'][0]['audio_summary']['analysis_url']
            analysis_response = urllib2.urlopen(analysis_url).read()
            analysis_response = json.loads(analysis_response)
            segments = analysis_response['segments']
        return segments


    def _get_features_list(self, segments, mode):
        try:
            features = [s[mode] for s in segments]
            return features
        except Exception, e:
            print e
            return None


    def _process_loudness_list(self, loudness_list):
        loudness_list = np.array(loudness_list)
        loudness_list += min(loudness_list) * -1
        l_max = max(loudness_list)
        loudness_list = [((ll**2)/(self.scale_factor*l_max)) for ll in loudness_list]
        return loudness_list


    def _rescale_list(self, input_list, a, b):
        input_max = max(input_list)
        rescale_factor = (b - a) / float(input_max)
        for i in xrange(len(input_list)):
            input_list[i] *= rescale_factor
        return input_list


    def make_waveform_square(self, waveform, n_bars_to_merge=1):
        res_waveform = None
        if len(waveform) > 0:
            res_waveform = []
            stored_wf_val = waveform[0]
            for i in xrange(1,len(waveform)):
                curr_wf_val = waveform[i]
                if i % n_bars_to_merge == 0:
                    stored_wf_val = curr_wf_val
                res_waveform.append(stored_wf_val)
        return res_waveform


    def make_waveform_3d(self, waveform, height):
        print "Creating the 3D waveform"
        n = len(waveform)  # number of bars
        m = int(ceil(max(waveform)))  # max bars height
        waveform_3d = np.zeros(shape=(2*m,n))
        min_loudness_value = max(waveform) / 10.0
        for i in xrange(m):  # for each row...
            res_row = []
            for j in xrange(n):  # for each column...
                curr_l_value = waveform[j] + min_loudness_value
                if i < curr_l_value:  # if we are in the "colored" part of the bar...
                    waveform_3d[m-i][j] = 1
                    waveform_3d[m+i][j] = 1
                else:  # if we are in the "hidden" part of the bar...
                    waveform_3d[m-i][j] = 0
                    waveform_3d[m+i][j] = 0
        # Scale height (i.e. Z axis)
        waveform_3d *= height
        return waveform_3d


    def _increase_model_depth(self, matrix, n):
        new_matrix = []
        for i in xrange(len(matrix)):  # for each column...
            new_col = []
            for j in xrange(len(matrix[i])):  # for each row...
                for k in xrange(n):  # for n times...
                    new_col.append(matrix[i][j])
            new_matrix.append(new_col)
        return new_matrix


    def online_music_3d(self, artist_name, track_name, mode="loudness_max"):
        """ Gets information from The Echo Nest services 
            and creates a 3D model of the input song.

        Args:
            artist_name: name of the artist
            track_name: name of the track
            mode: musical parameter to be used to create the 3D model
                  options: loudness_max, pitches, timbre

        """

        # Interact with The Echo Nest services
        self.en = pyen.Pyen(self.EN_API_KEY)
        print "Searching " + track_name + " by " + artist_name + " on The Echo Nest"
        audio_segments = self._get_segments(self.en, artist_name, track_name)
        if audio_segments is not None:
            audio_features = self._get_features_list(audio_segments, mode)

            if mode == 'loudness_max':  # waveform mode
                loudness_list = self._process_loudness_list(audio_features)
                loudness_list = self._rescale_list(loudness_list, 0, 100)
                processed_waveform = self.make_waveform_square(loudness_list, 
                                                          self.n_waveform_bars)
                model_3d = self.make_waveform_3d(processed_waveform, self.height)

            else:  # pitches or timbre
                new_features = []
                for af in audio_features:
                    new_features.append(self._rescale_list(af, self.min_absolute_value, self.height))
                new_features = self._increase_model_depth(new_features, self.depth_factor)
                model_3d = np.array(new_features)

            # Export 3D model
            if self.OUTPUT_FOLDER[-1] != '/':
                self.OUTPUT_FOLDER.append('/')
            output_filename = self.OUTPUT_FOLDER + artist_name + " - " + track_name + "_" + mode + ".stl"
            numpy2stl(model_3d, 
                      output_filename,
                      scale=self.scale, 
                      mask_val=self.mask_val, 
                      solid=True)


    def local_audio_3d(self, filepath, mode="waveform"):
        """ Converts a local audio file into a 3D model.

        Args:
            filepath: string containing the path to the audio file
            mode: musical parameter to be used to create the 3D model
                  options: waveform, stft
        """

        print "Loading audio file " + filepath
        waveform, sr = librosa.load(filepath)

        if mode == "waveform":  # time domain analysis
            # Downsample waveform and store positive values only
            if len(waveform) > 1000:
                m = len(str(len(waveform)))
                downsample_factor = 10 ** (m-1-3)  # 1k (i.e. 10^3) magnitude
            else:
                downsample_factor = 1
            half_waveform = [waveform[i] for i in xrange(len(waveform)) if waveform[i]>0 and i%downsample_factor==0]

            # Rescale waveform
            half_waveform = self._rescale_list(half_waveform, 0, 100)
            processed_waveform = self.make_waveform_square(half_waveform, self.n_waveform_bars)  # make waveform "square"

            # Convert 2D waveform into 3D
            print "Creating 3D model"
            model_3d = self.make_waveform_3d(processed_waveform, self.height)

        else:  # frequency domain analysis
            self.mask_val /= 100
            # Get STFT magnitude
            print "Analyzing frequency components"
            stft = librosa.stft(waveform, n_fft=256)
            stft, phase = librosa.magphase(stft)
            # Downsample and rescale STFT
            if len(stft[0]) > 1000:
                m = len(str(len(stft[0])))
                downsample_factor = (10 ** (m-1-3)) * int(str(len(stft[0]))[0])  # 1k (i.e. 10^3) magnitude
            else:
                downsample_factor = 1
            new_stft = []
            for curr_fft in stft:
                min_loudness_value = max(curr_fft)
                ds_fft = [curr_fft[j] + min_loudness_value for j in xrange(len(curr_fft)) if j%downsample_factor==0]
                ds_fft = self._rescale_list(ds_fft, self.min_absolute_value, self.height)
                new_stft.append(ds_fft)
            model_3d = np.array(new_stft)

        print "Exporting the 3D file"
        if self.OUTPUT_FOLDER[-1] != '/':
            self.OUTPUT_FOLDER.append('/')
        output_filename = self.OUTPUT_FOLDER + filepath.split('/')[-1][:-4] + "_" + mode + ".stl"
        numpy2stl(model_3d, 
                  output_filename, 
                  scale=self.scale, 
                  mask_val=self.mask_val, 
                  solid=True)
