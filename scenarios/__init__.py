import os
import random
from docx import Document
from mininet.clean import cleanup
from mininet.cli import CLI
from mininet.log import info, setLogLevel
from mininet.net import Containernet
from mininet.node import Controller, OVSSwitch

import document
from container.kali import Kali


class Scenario(object):

    def __init__(self, teacher=False, developer=False, seed=None):
        self.teacher = teacher
        self.developer = developer
        self.net = None
        self.seed = seed
        self.answerDocument = None
        self.taskDocument = None
        # Give the scenario a default name if we haven't one already
        if not hasattr(self, "name"):
            self.name = "scenario"

    def run(self):
        # Use the inputted seed, if given, to randomise the network
        if self.seed is not None:
            random.seed(self.seed)
        # Default to only error log printing for students
        setLogLevel('error')
        if self.teacher:
            # Allow teaches to see more complete logs
            setLogLevel('info')
        if self.developer:
            # Show debug logs for development
            setLogLevel('debug')
        # Create Containernet network
        self.createNetwork()
        # Generate task/answer sheets
        self.answerDocument = self.generateAnswers(self.answerDocument)
        self.taskDocument = self.generateTask(self.taskDocument)
        self.saveDocuments()
        # Start Containernet network
        self.runNetwork()
        return

    def createNetwork(self):
        info('*** Running Cleanup\n')
        cleanup()
        self.net = Containernet(controller=Controller)
        info('*** Adding controller\n')
        self.net.addController('c0')

    def generateAnswers(self, doc=Document()):
        return document.writeAnswers(self.net, doc)

    def generateTask(self, doc=Document()):
        doc.add_heading('Default Task document for %s.' % self.name, level=2)
        doc.add_paragraph(
            'If you are a student and weren\'t expecting to see this document, please contact your teacher.')
        doc.add_paragraph(
            'If you are a developing a scenario you are seeing this as you haven\'t yet overridden the generateTask() function')
        return doc

    # TODO: Permenant locations for answers/task
    # TODO: These parametes may be best used as fields in __init__ for flexibility/clarity
    def saveDocuments(self, studentDirectory='./student/', teacherDirectory='./teacher/', studentAllowedAnswers=False,
                      staticTaskDocument=True):
        """

        :param studentDirectory: Location of the student-accessible folder on the VM
        :type studentDirectory: string

        :param teacherDirectory: Location of the teacher-accessible folder on the VM
        :type teacherDirectory: string

        :param studentAllowedAnswers: Is the student provided the answer document for the task.
        :type studentAllowedAnswers: bool

        :param staticTaskDocument: Is the task document the same for every student.
        :type staticTaskDocument: bool
        """
        # Create neccisary directories if they do not exist
        for directory in [studentDirectory, teacherDirectory]:
            if not os.path.exists(directory):
                os.makedirs(directory)

        # -- Answer sheet --

        # Only generate the answer document if we're running as a teacher, or giving the student answers
        if self.teacher or studentAllowedAnswers:
            answerDocument = document.writeAnswers(self.net, self.answerDocument)
            # If we're a teacher, generate a document named "[Scenario name]-[Stduent ID].docx"
            if self.teacher:
                answerDocument.save(teacherDirectory + self.name + '-' + self.seed + '.docx')
            # If we're a student, generate a document named "[Scenario name]-answers.docx"
            else:
                answerDocument.save(studentDirectory + self.name + '-answers.docx')

        # -- Task sheet --

        # If the task sheet is the same for all students
        if staticTaskDocument:
            # And we're a teacher
            if self.teacher:
                # And we haven't created the task sheet yet
                taskLocation = teacherDirectory + self.name + '.docx'
                if not os.path.isfile(taskLocation):
                    # Create the task sheet
                    self.taskDocument.save(taskLocation)
        # If we're a student
        if not self.teacher:
            self.taskDocument.save(studentDirectory + self.name + '.docx')

    def runNetwork(self):
        # Start the Containernet network
        self.net.start()
        if self.developer:
            # If we're a developer, start the CLI
            # so we can test from the command line
            CLI(self.net)
            self.net.stop()


class ExampleScenario(Scenario):
    def __init__(self):
        # Override init to set developer to true
        Scenario.__init__(self, developer=True)

    def createNetwork(self):
        Scenario.createNetwork(self)
        # Add switch
        switch = self.net.addSwitch('s1', cls=OVSSwitch)
        # Add Kali
        kali = self.net.addDocker('kali', cls=Kali)
        self.net.addLink(switch, kali)
        # Add hosts
        for hostNum in range(0, random.randint(2, 25)):
            host = self.net.addHost('h' + str(hostNum))
            self.net.addLink(switch, host)

    def generateAnswers(self, doc=Document()):
        # Add a paragraph
        doc.add_paragraph("Just an example network, have fun!")
        # Run the normal answer generation
        return Scenario.generateAnswers(self, doc)

    def generateTask(self, doc=Document()):
        # Add a paragraph
        doc.add_paragraph("Just an example network, have fun!")
        # Just return without generating the default warning message document
        return doc

    def saveDocuments(self, **kwargs):
        # Simplify arguments list
        # Set students to gen the answer document, as an example
        kwargs["studentAllowedAnswers"] = True
        Scenario.saveDocuments(self, **kwargs)


if __name__ == "__main__":
    ExampleScenario().run()
