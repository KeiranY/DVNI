import logging
import os
import random

from docx import Document
from mininet.clean import cleanup, killprocs, Cleanup
from mininet.cli import CLI
from mininet.log import info, setLogLevel
from mininet.net import Containernet
from mininet.node import Controller, OVSSwitch
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import MultiprocessFTPServer

from container.kali import Kali
from controller import PoxController
from utils import document

from typing import List, Tuple

# Add a cleanup command to mininet.clean to clean pox controller
Cleanup.addCleanupCallback(lambda: killprocs(PoxController.poxCmd))


class Scenario(object):
    # These attributes allow for the filtering/ordering of scenarios when presenting them to students
    enabled = False
    weight = -1

    net = None  # type: Containernet

    def __init__(self, teacher=False, developer=False, seed=None):
        self.teacher = teacher
        self.developer = developer
        self.net = None
        self.seed = seed
        self.answer_document = Document()
        self.task_document = Document()
        # Give the scenario a default name if we haven't one already
        if not hasattr(self, "name"):
            self.name = "scenario"
        # Use the inputted seed, if given, to randomise the network
        if self.seed is not None:
            random.seed(self.name + self.seed)
            # If no seed, set seed to "random"
            # to indicate the outputted docuemnts are for a random seed
        else:
            self.seed = "random"

    def run(self):
        # Default to only error log printing for students
        setLogLevel('error')
        if self.teacher:
            # Allow teaches to see more complete logs
            setLogLevel('info')
        if self.developer:
            # Show debug logs for development
            setLogLevel('debug')
        # Create Containernet network
        self.create_network()
        # Start Containernet network
        self.run_network()
        # Generate task/answer sheets
        self.generate_task(self.task_document)
        self.generate_questions()
        self._add_questions(self.task_document)
        self._add_answers(self.answer_document)
        self.save_documents()
        if self.developer:
            # If we're a developer, start the CLI
            # so we can test from the command line
            CLI(self.net)
            self.net.stop()
        return

    def create_network(self, controller=Controller):
        info('*** Running Cleanup\n')
        cleanup()
        self.net = Containernet(controller=controller)
        if controller is not None:
            self.add_controller()

    def add_controller(self):
        self.net.addController()

    questions = []  # type: List[Tuple[str, str]]

    def _add_answers(self, doc):
        for idx, question in enumerate(self.questions):
            doc.add_paragraph(str(idx+1)+'. '+question[0]+': ').add_run(question[1]).bold=True

    def generate_task(self, doc):
        doc.add_heading('%s' % self.name, level=2)
        kali = self.net.get('kali')  # type: Kali
        if kali:
            kali.add_hint(doc)

    def generate_questions(self):
        pass

    def _add_questions(self, doc):
        for idx, question in enumerate(self.questions):
            doc.add_paragraph(str(idx+1)+'. '+question[0]+'? ')

    def save_documents(self, studentDirectory='./student/', teacherDirectory='./teacher/', studentAllowedAnswers=False,
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

        # For teachers, generate a document named "[Scenario name]-[Stduent ID].docx"
        self.answer_document.save(teacherDirectory + self.name + '-' + self.seed + '.docx')
        # If we're a student, generate a document named "[Scenario name]-answers.docx"
        if studentAllowedAnswers:
            self.answer_document.save(studentDirectory + self.name + '-answers.docx')

        # -- Task sheet --

        # If the task sheet is the same for all students
        if staticTaskDocument:
            taskLocation = teacherDirectory + self.name + '.docx'
            # Create the task sheet
            self.task_document.save(taskLocation)
        # If we're a student
        #if not self.teacher:
        self.task_document.save(studentDirectory + self.name + '.docx')

    def run_ftp(self, studentDirectory='./student/', teacherDirectory='./teacher'):
        authorizer = DummyAuthorizer()
        pw = '%05x' % random.randrange(16 ** 5)
        if self.teacher:
            authorizer.add_user(username="teacher", password=pw, homedir=teacherDirectory)
        else:
            authorizer.add_user(username="student", password=pw, homedir=studentDirectory)
        handler = FTPHandler
        handler.authorizer = authorizer

        handler.banner = "DVNG tasks ftp server"

        # Instantiate FTP server class and listen on 0.0.0.0:2121
        address = ('', 21)
        server = MultiprocessFTPServer(address, handler)

        # set a limit for connections
        server.max_cons = 256
        server.max_cons_per_ip = 5

        # start ftp server
        print("Task sheets are available over ftp on port 21\n" +
              "\tUsername: %s\n" % ("teacher" if self.teacher else "student") +
              "\tPassword: %s\n" % pw +
              "Keep this terminal open until you've retreived your files.")
        logging.basicConfig(level=logging.CRITICAL)
        server.serve_forever()

    def run_network(self):
        # Start the Containernet network
        self.net.start()
