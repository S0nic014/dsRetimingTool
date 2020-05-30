import pymel.core as mc
import maya.cmds as mc
import maya.mel as mel


class RetimeUtils(object):

    @classmethod
    def retimeKeys(cls, retimeValue, isIncremental, moveToNext):
        rangeStartTime, rangeEndTime = cls.getSelectedRange()
        startKeyframeTime = cls.getStartKeyframeTime(rangeStartTime)
        lastKeyframe = cls.getLastKeyframeTime()
        currentTime = startKeyframeTime

        newKeyframeTimes = [startKeyframeTime]
        while currentTime != lastKeyframe:
            nextKeyframeTime = cls.findKeyframe("next", currentTime)
            if isIncremental:
                timeDelta = nextKeyframeTime - currentTime
                if currentTime < rangeEndTime:
                    timeDelta += retimeValue
                    if timeDelta < 1:
                        timeDelta = 1
            else:
                if currentTime < rangeEndTime:
                    timeDelta = retimeValue
                else:
                    timeDelta = nextKeyframeTime - currentTime

            newKeyframeTimes.append(newKeyframeTimes[-1] + timeDelta)
            currentTime = nextKeyframeTime 

        if len(newKeyframeTimes) > 1:
            cls.retimeKeysRecursive(startKeyframeTime, 0, newKeyframeTimes)

        firstKeyframeTime = cls.findKeyframe("first")
        if moveToNext and rangeStartTime>=firstKeyframeTime:
            nextKeyframeTime = cls.findKeyframe("next", startKeyframeTime)
            cls.setCurrentTime(nextKeyframeTime)

        elif rangeEndTime > firstKeyframeTime:
            cls.setCurrentTime(startKeyframeTime)
            
        else:
            cls.setCurrentTime(rangeStartTime)

    
    @classmethod
    def retimeKeysRecursive(cls, currentTime, index, newKeyframeTimes):
        if index >= len(newKeyframeTimes):
            return
        
        updatedKeyframeTime = newKeyframeTimes[index]
        nextKeyframeTime = cls.findKeyframe("next", currentTime)
        if updatedKeyframeTime < nextKeyframeTime:
            cls.changeKeyframeTime(currentTime, updatedKeyframeTime)
            cls.retimeKeysRecursive(nextKeyframeTime, index+1, newKeyframeTimes)
        else:
            cls.retimeKeysRecursive(nextKeyframeTime, index+1, newKeyframeTimes)
            cls.changeKeyframeTime(currentTime, updatedKeyframeTime)
            


    @classmethod
    def setCurrentTime(cls, time):
        mc.currentTime(time)

        return time


    @classmethod
    def getSelectedRange(cls):
        playbackSlider = mel.eval("$tempVar = $gPlayBackSlider")
        selectedRange = mc.timeControl(playbackSlider, q=1, rangeArray=1)

        return selectedRange


    @classmethod
    def findKeyframe(cls, which, time=None):
        kwargs = {"which" : which}
        if which in ["next", "previous"]:
            kwargs["time"] = (time, time)

        return mc.findKeyframe(**kwargs)


    @classmethod
    def changeKeyframeTime(cls, currentTime, newTime):
        mc.keyframe(e=1, time=(currentTime, currentTime), timeChange=newTime)


    @classmethod
    def getStartKeyframeTime(cls, rangeStartTime):
        startTimes = mc.keyframe(time=(rangeStartTime, rangeStartTime), q=1)
        if startTimes:
            return startTimes[0]
        
        startTime = cls.findKeyframe("previous", rangeStartTime)

        return startTime


    @classmethod
    def getLastKeyframeTime(cls):
        return cls.findKeyframe("last")





if __name__ == "__main__":
    RetimeUtils.retimeKeys(2, False, False)