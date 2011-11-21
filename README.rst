wffmpeg
======================

Basic usage
==========

    >>> from wffmpeg import FFDocument
    >>> with video = open('example.mp4'):
    >>>     video_data = video.read()
    >>>     video_document = FFDocument(str(video_data))
    
Installing
==========

On unix-based systems::
   sudo python setup.py install

On windows::
   python setup.py install

Contributing
============

With new features
^^^^^^^^^^^^^^^^^

 1. Create both unit and functional tests for your new feature
 2. Do not let the coverage go down, 100% is the minimum.
 3. Write properly documentation
 4. Send-me a patch with: ``git format-patch``

E-mail: marcel.nicolay at gmail com
