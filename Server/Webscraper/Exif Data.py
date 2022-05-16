import math

class ExifData():
    byteArray = []
    def __init__(self, fileName):
        f = open(fileName,"rb")

        #test = [byte & 1 for byte in bytearray(f.read(100))]
        test = bytearray(f.read())
        print(test)
        self.byteArray = f.read()
        f.close()

    def LoadData(self):
        print(self.byteArray)
        if self.byteArray[0] != 255 or self.byteArray[1] != 216:
            return

        endExif = self.EndExifIndex(2)
        titleIndex = self.FindIndex([156, 155], 0)
        if titleIndex != -1 and titleIndex < endExif:
            titleOffset = self.ToInt(self.ToHex(self.byteArray[titleIndex + 10], "") + self.ToHex(self.byteArray[titleIndex + 11], ""), 0, 0) + 9
            titleLength = self.ToInt(self.ToHex(self.byteArray[titleIndex + 6], "") + self.ToHex(self.byteArray[titleIndex + 7], ""), 0, 0)
            title = self.byteArray[titleOffset + 3 : titleLength - 2].decode('UTF-32')

        subjectIndex = self.FindIndex([156, 159], 0)
        if subjectIndex != -1 and subjectIndex < endExif:
            subjectOffset = self.ToInt(self.ToHex(self.byteArray[subjectIndex + 10], "") + self.ToHex(self.byteArray[subjectIndex + 11], ""), 0, 0) + 9
            subjectLength = self.ToInt(self.ToHex(self.byteArray[subjectIndex + 6], "") + self.ToHex(self.byteArray[subjectIndex + 7], ""), 0, 0)
            subject = self.byteArray[subjectOffset + 3 : subjectLength - 2].decode('UTF-32')

        userCommentIndex = self.FindIndex([156, 159], 0)
        if userCommentIndex != -1 and userCommentIndex < endExif:
            userCommentOffset = self.ToInt(self.ToHex(self.byteArray[userCommentIndex + 10], "") + self.ToHex(self.byteArray[userCommentIndex + 11], ""), 0, 0) + 12
            userCommentLength = self.ToInt(self.ToHex(self.byteArray[userCommentIndex + 6], "") + self.ToHex(self.byteArray[userCommentIndex + 7], ""), 0, 0)
            userComment = self.byteArray[subjectOffset + 8 : subjectLength - 8].decode('UTF-32')

    def EndExifIndex(self, startIndex):
        return startIndex if self.byteArray[startIndex] == 255 and self.byteArray[startIndex + 1] == 219 else self.EndExifIndex(
            startIndex + self.ToInt(self.ToHex(self.byteArray[startIndex + 2], "") + self.ToHex(self.byteArray[startIndex + 3], ""), 0, 0) + 2)

    def FindIndex(self, query, startindex):
        if startindex + len(query) >= len(self.byteArray):
            return -1

        index = self.byteArray.index(query[0], startindex)
        if index == -1: return -1
        for a in range(1, len(query)):
            if self.byteArray[index + a] != query[a]:
                return self.FindIndex(query, index + 1)
        
        return index

    def ToInt(self, hexSting, value, pos):
        if pos == len(hexSting): return value

        if hexSting[pos] == 'A':
            return self.ToInt(hexSting, value + 10 * int(math.pow(16, len(hexSting) - (pos + 1))), pos =+1)
        elif hexSting[pos] == 'B':
            return self.ToInt(hexSting, value + 11 * int(math.pow(16, len(hexSting) - (pos + 1))), pos =+1)
        elif hexSting[pos] == 'C':
            return self.ToInt(hexSting, value + 12 * int(math.pow(16, len(hexSting) - (pos + 1))), pos =+1)
        elif hexSting[pos] == 'D':
            return self.ToInt(hexSting, value + 13 * int(math.pow(16, len(hexSting) - (pos + 1))), pos =+1)
        elif hexSting[pos] == 'E':
            return self.ToInt(hexSting, value + 14 * int(math.pow(16, len(hexSting) - (pos + 1))), pos =+1)
        elif hexSting[pos] == 'F':
            return self.ToInt(hexSting, value + 15 * int(math.pow(16, len(hexSting) - (pos + 1))), pos =+1)
        else:
            return self.ToInt(hexSting, value * int(math.pow(16, len(hexSting) - (pos + 1))), pos =+1)

    def ToHex(self, value, hexString):
        if value == 0: return hexString

        if value % 16 == 10:
            return self.ToHex(value / 16, "A" + hexString)
        elif value % 16 == 11:
            return self.ToHex(value / 16, "B" + hexString)
        elif value % 16 == 12:
            return self.ToHex(value / 16, "C" + hexString)
        elif value % 16 == 13:
            return self.ToHex(value / 16, "D" + hexString)
        elif value % 16 == 14:
            return self.ToHex(value / 16, "E" + hexString)
        elif value % 16 == 15:
            return self.ToHex(value / 16, "F" + hexString)
        elif value % 16 == 0:
            return "0" if value == 0 else self.ToHex(value / 16, "0" + hexString)
        else:
            return self.ToHex(value / 16, value % 16 + hexString)

    def SaveData(self):
        pass


a = ExifData("C:\\Users\\remon\\Desktop\\test.jpeg")
a.LoadData()