import os


class rttmWriter:

    def __init__(self, convFile, outputFolder):
        self.convFile = convFile
        self.outputFolder = outputFolder

    def writeRTTM(self):
        """Write RTTM file."""
        print("Generate RTTM for",self.convFile.file_path)
        outputFile = os.path.join(self.outputFolder, "conversation.rttm")
        with open(outputFile, "w") as f:
            for line in self.convFile.lines:
                f.write(f"{line.type} {line.audioFileRelativePath} 1 {line.offset} {line.duration} <NA> {line.subtype} {line.speaker} <NA> <NA>\n")
            f.close()
        print("RTTM file written to", outputFile)