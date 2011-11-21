from wffmpeg.ffbase import FFVideoEffect, FFAudioEffect, FFmpeg

class FFDocument(FFVideoEffect, FFAudioEffect):
    """
        audio/video document. A FFDocument describe a higer level action set
        combining several FF[Audio|Video]Effect methods. 
    """

    def __init__(self, file, metadata=None, effects={}):
        """
            x.__init__(...) initializes x; see x.__class__.__doc__ for signature
        """
        FFAudioEffect.__init__(self, file)
        FFVideoEffect.__init__(self, file, **effects)
        if not metadata:
            self.__metadata__ = FFmpeg().info(file)[0]
        else:
            self.__metadata__ = metadata

    def __tlen__(self):
        """
            return time length
        """
        t = self.__timeparse__(self.__metadata__["duration"])
        if self.seek():
            t = t - self.seek()
        if self.duration():
            t = t - (t - self.duration())
        return t

    def __timereference__(self, reference, time):
        if type(time) == str:
            if '%' in time:
                parsed = (reference / 100.0) * int(time.split("%")[0])
            elif len(time.split(':')) == 3:
                hhn, mmn, ssn = [float(i) for i in  time.split(":")]
                parsed = hhn * 3600 + mmn * 60 + ssn
        else:
            parsed = time
        return parsed

    def __timeparse__(self, time):

        hh, mm, ss = [float(i) for i in  time.split(":")]
        return hh * 3600 + mm * 60 + ss

    def __clone__(self):
        return FFDocument(self.__file__, self.__metadata__.copy(), self.__effects__.copy())

    def resample(self, width=0, height=0, vstream=0):
        """ 
            adjust video dimensions. If one dimension
            is specified, the resampling is proportional
        """
        w, h = [int(i) for i in  self.__metadata__["video"][vstream]["size"][0].split("x")]
        if not width:
            width = int(w * (float(height) / h))
        elif not height:
            height = int(h * (float(width) / w))
        elif not width and height:
            return

        new = self.clone()
        if width < w:
            cropsize = (w - width)/2
            new.crop(0, 0, cropsize, cropsize)
        elif width > w:
            padsize = (width - w)/2
            new.pad(0, 0, padsize, padsize)
        if height < h:
            cropsize = (h - height)/2
            new.crop(cropsize, cropsize, 0, 0)
        elif height > h:
            padsize = (height - h)/2
            new.pad(padsize, padsize, 0, 0)
        return new

    def resize(self, width=0, height=0, vstream=0): 
        """ 
            resize video dimensions. If one dimension
            is specified, the resampling is proportional
            
            width and height can be pixel or % (not mixable)
        """
        w, h = [int(i) for i in  self.__metadata__["video"][vstream]["size"][0].split("x")]
        if type(width) == str or type(height) == str:
            if not width:
                width = height = int(height.split("%")[0])
            elif not height:
                height = width = int(width.split("%")[0])
            elif not width and height:
                return
            elif width and height:
                width = int(width.split("%")[0])
                height = int(height.split("%")[0])
            size = "%sx%s"  % (int(w / 100.0 * width), int(h / 100.0 * height))
        else:
            if not width:
                width = int(w * (float(height) / h))
            elif not height:
                height = int(h * (float(width) / w))
            elif not width and height:
                return
            size = "%sx%s" % (width, height)
        new = self.__clone__()
        new.size(size)
        return new

    def split(self, time):
        """ 
            return a tuple of FFDocument splitted at
            a specified time.
            allowed formats: %, sec, hh:mm:ss.mmm
        """
        sectime = self.__timeparse__(self.__metadata__["duration"])
        if self.duration():
            sectime = sectime - (sectime - self.duration())
        if self.seek():
            sectime = sectime - self.seek()
        cut = self.__timereference__(sectime, time)

        first = self.__clone__() 
        second = self.__clone__()
        first.duration(cut)
        second.seek(cut + 0.001)
        return first, second

    def ltrim(self, time):
        """ 
            trim leftmost side (from start) of the clip
        """
        sectime = self.__timeparse__(self.__metadata__["duration"])
        if self.duration():
            sectime = sectime - (sectime - self.duration())
        if self.seek():
            sectime = sectime - self.seek()
        trim = self.__timereference__(sectime, time)
        new = self.__clone__()
        if self.seek():
            new.seek(self.seek() + trim)
        else:
            new.seek(trim)
        return new

    def rtrim(self, time):
        """
            trim rightmost side (from end) of the clip
        """
        sectime = self.__timeparse__(self.__metadata__["duration"])
        if self.duration():
            sectime = sectime - (sectime - self.duration())
        if self.seek():
            sectime = sectime - self.seek()
        trim = self.__timereference__(sectime, time)
        new = self.__clone__()
        new.duration(trim)
        return new
        
    def trim(self, left, right):
        """
            left and right trim (actually calls ltrim and rtrim)
        """
        return self.__clone__().ltrim(left).rtrim(right)

    def chainto(self, ffdoc):
        """
            prepare to append at the end of another movie clip
        """
        offset = 0
        if ffdoc.seek():
            offset = ffdoc.seek()
        if ffdoc.duration():
            offset = offset + ffdoc.seek()
        if ffdoc.offset():
            offset = offset + ffdoc.offset()

        new = self.__clone__()
        new.offset(offset)
        return new

    #TODO: more and more effects!!!
