from dataclasses import dataclass
from pedalboard.io import AudioFile
import os

@dataclass
class conversationFileLine:
    """Dataclass for a single line in a conversation file."""
    audioFile: str
    audioFilePath: str
    audioFileRelativePath: str    
    offset: float
    type: str
    subtype: str
    speaker: str
    text_description: str
    duration: float = 0.0
    startSample: int = 0
    endSample: int = 0


class conversationFile:
    def __init__(self, file_path):
        self.file_path = file_path
        self.inputFolder = os.getcwd()
        self.lines = []
        self.readConversation()
        self.sampleRate = self.getSampleRate()
        if self.sampleRate == 0:
            raise ValueError("Sample rates are not equal.")
        self.speakers = self.getSpeakers()
        self.calculateTiming()
        self.endOfSpeech = self.getEndOfSpeech()
        self.totalDuration = self.endOfSpeech + 2 # add two seconds after the last speech ends
        self.sampleCount = int(self.totalDuration * self.sampleRate)

    def readConversation(self):
        with open(self.file_path, "r") as f:
            next(f)  # Skip the first line
            for line in f:
                self.lines.append(self.parseLine(line))
    
    def parseLine(self, line):
        parts = line.split(";")
        if len(parts) != 7:
            raise ValueError(f"Line in conversation file {self.file_path} has {len(parts)} parts, expected 7.")
        if " " in parts[0]:
            raise ValueError(f"Invalid audio file path in conversation file {self.file_path}: {parts[0]}.")
        if " " in parts[1]:
            raise ValueError(f"Invalid audio file name in conversation file {self.file_path}: {parts[1]}.")
        audioFilePath = os.path.join(self.inputFolder, parts[0], parts[1])
        
        return conversationFileLine(
            audioFile=parts[1],
            audioFilePath=audioFilePath,
            audioFileRelativePath=os.path.join(parts[0], parts[1]),
            offset=float(parts[2]),
            type=parts[3],
            subtype=parts[4],
            speaker=parts[5],
            text_description=parts[6].replace('\n', ''))
    
    def calculateTiming(self):
        """Calculate conversation timing."""
        for line in self.lines:
            startSample = int(line.offset * self.sampleRate)
            endSample = self.getAudioFileLength(line.audioFilePath) + startSample
            duration = round((self.getAudioFileLength(line.audioFilePath) / self.getSampleRate()),6)
            line.startSample = startSample
            line.endSample = endSample
            line.duration = duration

    
    def printInfo(self):
        print(f"Conversation file at {self.file_path}")
        print(f"- Lines {len(self.lines)}")
        print(f"- Sample rate: {self.sampleRate} Hz")
        print(f"- Total duration: {self.totalDuration} s")
        print(f"- End of speech: {self.endOfSpeech} s")
        print(f"- Total sample count: {self.sampleCount}")
        print(f"- Line count: {self.getLineCount()}")
        print(f"- Speakers: {self.speakers}")
        

    def printLines(self):
        for line in self.lines:
            print(line)
    
    def getEndOfSpeech(self):
        return round(max([(line.offset+line.duration) for line in self.lines if line.type == "SPEAKER"]),6)
    
    def getLineCount(self):
        return len(self.lines)
    
    def getAudioFiles(self):
        return [line.audioFilePath for line in self.lines]
    
    def getSpeakers(self):
        return list(set([line.speaker for line in self.lines if line.type == "SPEAKER"]))
    
    def getLinesForSpeaker(self, speaker):
        return [line for line in self.lines if line.speaker == speaker]
    
    def getSampleRate(self):
        audioFiles = self.getAudioFiles()
        sampleRates = []
        audioFileNames = []
        for audioFile in audioFiles:
            audioFileNames.append(os.path.relpath(audioFile))
            with AudioFile(audioFile) as af:
                sampleRates.append(af.samplerate)
        if all(sampleRate == sampleRates[0] for sampleRate in sampleRates):
            return sampleRates[0]
        else:
            print ("Sample rates are NOT equal:")
            for i in range(len(audioFiles)):
                print(f"{sampleRates[i]} Hz: {audioFileNames[i]}")
            return 0
    
    def getAudioFileLength(self, audioFile):
        with AudioFile(audioFile) as af:
            return af.frames
            