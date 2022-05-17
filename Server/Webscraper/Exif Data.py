import math
import numpy as np

class ExifData():
    byteArray = []
    def __init__(self, fileName):
        f = open(fileName,"rb")
        dtype = np.dtype('B')
        self.byteArray = np.fromfile(f,dtype)
        self.byteArray = self.byteArray.tolist()
        f.close()

    #this function looks for the markers for 2 exif data tags using the tiff standard.
    #Title is the first tag with 156 and 155 in dec as identifier
    #then it reads the offset of the data for this tag.
    #after that we look for the length of said data and then we read it adn convert it to a string by removing the zeros and converting it tom a utf8 string
    #we do the same thing for the exif tag subject but not for the tag userComment because there are no zeros in the data unless specified
    def LoadData(self):
        if self.byteArray[0] != 255 or self.byteArray[1] != 216:
            return

        endExif = self.EndExifIndex(2)
        titleIndex = self.FindIndex([156, 155], 0)
        if titleIndex != -1 and titleIndex < endExif:
            titleOffset = self.ToInt(self.ToHex(self.byteArray[titleIndex + 10], "") + self.ToHex(self.byteArray[titleIndex + 11], ""), 0, 0) + 9
            titleLength = self.ToInt(self.ToHex(self.byteArray[titleIndex + 6], "") + self.ToHex(self.byteArray[titleIndex + 7], ""), 0, 0)
            title = bytearray([i for i in self.byteArray[titleOffset + 3 : titleOffset + 3 + titleLength - 2] if i != 0]).decode('utf8')
            
        subjectIndex = self.FindIndex([156, 159], 0)
        if subjectIndex != -1 and subjectIndex < endExif:
            subjectOffset = self.ToInt(self.ToHex(self.byteArray[subjectIndex + 10], "") + self.ToHex(self.byteArray[subjectIndex + 11], ""), 0, 0) + 9
            subjectLength = self.ToInt(self.ToHex(self.byteArray[subjectIndex + 6], "") + self.ToHex(self.byteArray[subjectIndex + 7], ""), 0, 0)
            subject = bytearray([i for i in self.byteArray[subjectOffset + 3 : subjectOffset + 3 + subjectLength - 2] if i != 0]).decode('utf8')

        userCommentIndex = self.FindIndex([146, 134], 0)
        if userCommentIndex != -1 and userCommentIndex < endExif:
            userCommentOffset = self.ToInt(self.ToHex(self.byteArray[userCommentIndex + 10], "") + self.ToHex(self.byteArray[userCommentIndex + 11], ""), 0, 0) + 12
            userCommentLength = self.ToInt(self.ToHex(self.byteArray[userCommentIndex + 6], "") + self.ToHex(self.byteArray[userCommentIndex + 7], ""), 0, 0)
            userComment = bytearray(self.byteArray[userCommentOffset + 8 : userCommentOffset + 8 + userCommentLength - 8]).decode('utf8')

        return title + "\n" + subject + "\n" + userComment

    #this function looks for the hexadecimals FF DB. This is a marker for the end of an exif block. It can find the marker using the exif length which is
    #specified in the folowing 2 bytes after FF EX.
    def EndExifIndex(self, startIndex):
        return startIndex if self.byteArray[startIndex] == 255 and self.byteArray[startIndex + 1] == 219 else self.EndExifIndex(
            startIndex + self.ToInt(self.ToHex(self.byteArray[startIndex + 2], "") + self.ToHex(self.byteArray[startIndex + 3], ""), 0, 0) + 2)

    #this function searches for the first occurence of the list query starting from the startindex. If there is no occurence it returns -1
    #query is immutable. This means that the data has to be in the same order as in query
    def FindIndex(self, query, startindex):
        if startindex + len(query) >= len(self.byteArray):
            return -1

        index = self.byteArray.index(query[0], startindex)
        if index == -1: return -1
        for a in range(1, len(query)):
            if self.byteArray[index + a] != query[a]:
                return self.FindIndex(query, index + 1)
        
        return index

    #this function can convert any hex string to an integer
    def ToInt(self, hexSting, value, pos):
        if pos == len(hexSting): return value

        if hexSting[pos] == 'A':
            return self.ToInt(hexSting, value + 10 * int(math.pow(16, len(hexSting) - (pos + 1))), pos + 1)
        elif hexSting[pos] == 'B':
            return self.ToInt(hexSting, value + 11 * int(math.pow(16, len(hexSting) - (pos + 1))), pos + 1)
        elif hexSting[pos] == 'C':
            return self.ToInt(hexSting, value + 12 * int(math.pow(16, len(hexSting) - (pos + 1))), pos + 1)
        elif hexSting[pos] == 'D':
            return self.ToInt(hexSting, value + 13 * int(math.pow(16, len(hexSting) - (pos + 1))), pos + 1)
        elif hexSting[pos] == 'E':
            return self.ToInt(hexSting, value + 14 * int(math.pow(16, len(hexSting) - (pos + 1))), pos + 1)
        elif hexSting[pos] == 'F':
            return self.ToInt(hexSting, value + 15 * int(math.pow(16, len(hexSting) - (pos + 1))), pos + 1)
        else:
            return self.ToInt(hexSting, value + int(hexSting[pos]) * int(math.pow(16, len(hexSting) - (pos + 1))), pos + 1)

    #this function can convert any integer to a hex string
    def ToHex(self, value, hexString):
        if value == 0: return hexString

        if value % 16 == 10:
            return self.ToHex(int(value / 16), "A" + hexString)
        elif value % 16 == 11:
            return self.ToHex(int(value / 16), "B" + hexString)
        elif value % 16 == 12:
            return self.ToHex(int(value / 16), "C" + hexString)
        elif value % 16 == 13:
            return self.ToHex(int(value / 16), "D" + hexString)
        elif value % 16 == 14:
            return self.ToHex(int(value / 16), "E" + hexString)
        elif value % 16 == 15:
            return self.ToHex(int(value / 16), "F" + hexString)
        elif value % 16 == 0:
            return "0" if value == 0 else self.ToHex(int(value / 16), "0" + hexString)
        else:
            return self.ToHex(int(value / 16), str(int(value % 16)) + hexString)

    def SaveData(self):
        pass


a = ExifData("C:\\Users\\remon\\Desktop\\test.jpeg")
print(a.LoadData())