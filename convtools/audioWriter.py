from pedalboard.io import AudioFile
from pedalboard import Reverb, Convolution, Resample, GSMFullRateCompressor, Bitcrush, Clipping
import numpy as np
import os

class audioWriter:
    def __init__(self, convFile, outputFolder):
        self.convFile = convFile
        self.outputFolder = outputFolder
        self.generateAudio()

    def generateAudio(self):
        print("Generate audio for",self.convFile.file_path)
        self.audio = np.zeros((1,self.convFile.sampleCount))
        for line in self.convFile.lines:
            print("- adding", line.audioFile)
            with AudioFile(line.audioFilePath) as af:
                audio = af.read(af.frames) # TODO: read chunks
                if (audio.shape[0] >1):
                    print("  Warning: audio has more than one channel, using only the first one.")
                    audio = audio[0]
                    audio.resize((1,audio.shape[0]))
                startSample = line.startSample
                if startSample < 0:
                    print("  Warning: negative offsets not supported, setting to 0.")
                    startSample = 0
                audio = np.concatenate((np.zeros((1,startSample)), audio), axis=1)
                audio.resize((1,self.convFile.sampleCount))
                self.audio = np.add(self.audio, audio)

    
    def writeAudio(self, fileName="output.mp3",**kwargs):
        print(f"Processing audio for {self.convFile.file_path}...")
        sr = self.convFile.sampleRate
        audio = np.copy(self.audio)
        if "reverb" in kwargs:
            audio = self.addReverb(audio, sr, room_size=kwargs["reverb"])
        if "environment" in kwargs:
            audio = self.addEnvironment(audio, sr, kwargs["environment"])
        if "bitrate" in kwargs:
            audio = self.addBitrate(audio, sr, kwargs["bitrate"])
        if "clipping" in kwargs:    
            audio = self.addClipping(audio, sr, kwargs["clipping"])
        if "transmission" in kwargs:
            audio = self.addTransmission(audio, sr, kwargs["transmission"])
        fileAndPath = os.path.join(self.outputFolder, fileName)
        with AudioFile(fileAndPath, mode="w", samplerate=sr) as af:
            af.write(audio)
        print("Audio saved to", fileAndPath, "with sample rate", sr)

    
    def addReverb(self, audio, sampleRate, room_size=0.75):
        print("- adding reverb with room size", room_size)
        reverb = Reverb(room_size=room_size)
        return reverb(audio,sampleRate)
    
    
    def addEnvironment(self, audio, sampleRate,environment):
        impulseResponse = os.path.join('convtools','ir', environment+'.wav')
        if not os.path.exists(impulseResponse):
            print("Error: file", impulseResponse, "not found.")
            return
        print("- adding environment", environment)
        convolution = Convolution(impulseResponse)
        return convolution(audio,sampleRate)
    
    def addTransmission(self, audio, sampleRate, channel):
        print("- resample for transmission by", channel)
        if channel == "phone":
            gsm = GSMFullRateCompressor()
            return gsm(audio,sampleRate)
        elif channel == "voip":
            resample = Resample(16000)
            return resample(audio,sampleRate)
        else:
            print("Error: transmission channel", channel, "not supported.")
            return audio
    
    def addBitrate(self, audio, sampleRate, bitrate):
        print("- set bitrate to", bitrate)
        bitCrush = Bitcrush(bitrate)
        return bitCrush(audio,sampleRate)
    
    def addClipping(self, audio, sampleRate, threshold=-6):
        print("- add clipping with threshold", threshold,"dB")
        clipping = Clipping(threshold)
        return clipping(audio,sampleRate)
    



    # Documentation of effects: https://spotify.github.io/pedalboard/reference/pedalboard.html#
    # impulse responses: https://www.openair.hosted.york.ac.uk/?page_id=36

    