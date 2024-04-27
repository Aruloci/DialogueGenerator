import os
import mytextgrid

# https://pypi.org/project/mytextgrid/
# https://mytextgrid.readthedocs.io/en/latest/api_reference.html
# pip install mytextgrid -U

class textGridWriter:

    def __init__(self, convFile, outputFolder):
        self.convFile = convFile
        self.outputFolder = outputFolder

    def writeTextGrid(self):
        """Write TextGrid file."""
        print("Generate TextGrid for",self.convFile.file_path)
        outputFile = os.path.join(self.outputFolder, "conversation.TextGrid")
        speakers = self.convFile.speakers 
        tg = mytextgrid.create_textgrid(xmin = 0, xmax = self.convFile.totalDuration)

        for speaker in speakers:
            tier = tg.insert_tier(speaker)
            lines = self.convFile.getLinesForSpeaker(speaker)
            boundaries, texts = self.calculateIntervals(lines)
            for boundary in boundaries:
                if boundary != 0:
                    tier.insert_boundaries(boundary)
            for i, text in enumerate(texts):
                tier.set_text_at_index(i,text)

        tg.write(outputFile)
        print("TextGrid file written to", outputFile)


    def calculateIntervals(self, lines):
        """Calculate intervals for interval-tiers."""
        boundaries = []
        texts = []
        currentTime = 0
        for line in lines:
            startTime = round(line.offset,3)
            endTime = round(line.offset + line.duration,6)
            if startTime > currentTime:
                boundaries.append(currentTime)
                texts.append("")
            boundaries.append(startTime)
            texts.append(line.text_description)
            currentTime = endTime
        boundaries.append(currentTime)
        return boundaries, texts
        

#  other text grid libraries

# https://pypi.org/project/praat-textgrids/
# pip install praat-textgrids

# https://github.com/kylebgorman/textgrid/blob/master/textgrid/textgrid.py
# pip install textgrid