
#
# Utilities functions for handling cooperative multitasking.
#

import filelike
import gevent
import sys
import termcolor


class OutCapture(filelike.FileLikeBase):
    """A file-like object that combines output from multiple tasks,
    distinguishing each with the name of the task.
    """
    task = None
    outTask = None
    inLine = False

    def __init__(self, baseFile):
        """Initialize the instance.

        Arguments:
            baseFile (filelike): File output where the combined out will be
              sent.
        """
        super(OutCapture, self).__init__()
        self.baseFile = baseFile

    def setTask(self, task):
        self.task = task

    def _write(self, data, flushing=False):
        """Handle a write from one of the tasks."""
        if not len(data):
            return

        if self.task != self.outTask:
            if self.inLine:
                self.baseFile.write('\n')
            self.baseFile.write(termcolor.colored(self.task.name, 'yellow') + ': ')
        elif not self.inLine:
            self.baseFile.write(termcolor.colored(self.task.name, 'yellow') + ': ')

        self.baseFile.write(data)
        self.outTask = self.task
        self.inLine = (data[-1] != '\n')


class TaskGreenlet(gevent.Greenlet):
    """A named task that redirects its output to an OutCapture."""

    outCapture = OutCapture(sys.stdout)

    def __init__(self, *args, **kw):
        self.name = kw.pop('name')
        super(TaskGreenlet, self).__init__(*args, **kw)

    def __repr__(self):
        """Display this task as its name."""
        return self.name

    def switch(self, *args):
        """Redirect the output for the task and switch to it."""
        self.outCapture.setTask(self)
        sys.stdout = self.outCapture
        super(TaskGreenlet, self).switch(*args)

