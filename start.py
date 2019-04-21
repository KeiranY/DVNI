import os
import importlib
import argparse
import sys

import random

from mininet.log import setLogLevel


def choice_from_list(l, name='item'):
    """
    Displays a list of options to the user and validates their choice as an integer within the bounds of the array.

    :param l: Items to be chosen from
    :type l: list(str)
    :param name: String to be shown to the user to describe the item they're choosing
    :return: The choice as an index of l
    """
    # Loop until a valid choice is made
    while True:
        # Print list of containers in l "[0] Container_name"
        for idx, container in enumerate(l):
            print("[%i] %s" % (idx, container))
        # Get user's choice
        try:
            choice = raw_input("Select a %s: " % name)
            choice = int(choice)
        except ValueError:
            # The conversion of choice to int has failed
            print("*** Please enter a valid number.")
            continue
        if choice < 0 or choice >= len(l):
            # The choice was outside the range
            print("*** Please enter a number in the range 0-%d." % (len(l) - 1))
            continue
        # The choice was valid, return it
        return choice


def main():
    """
        This file is executed when either the teacher of student user accounts are logged in.
        A parameter is passed to this script allowing us to discern what user we are running as.
    """

    def containers():
        # Get every container in the container folder
        containerdir = currentdir + "/container"
        choices = list(x for x in os.listdir(containerdir) if not os.path.isfile(os.path.join(containerdir, x)))
        # Get the user's chosen container
        index = choice_from_list(choices, 'container')
        # Import and run the container example
        importlib.import_module("container.%s.example" % choices[index])

    def test_scenarios():
        filtered_choices = [scenario for scenario in (c.Import for c in (importlib.import_module("scenarios.%s" % c) for c in (list(x[:-3] for x in os.listdir(currentdir + "/scenarios") if x[-3:] == ".py" and x[:2] != "__"))) if hasattr(c, 'Import')) if hasattr(scenario, 'enabled') and scenario.enabled]
        setLogLevel("error")
        for seed in range(5):
            for scenario in filtered_choices:
                print('*** %s SEED:%s' % (scenario.name, str(seed)))
                scenario(teacher=True, seed=str(seed)).run()

    def scenarios():
        # Get every scenario in the scenario folder
        scenariodir = currentdir + "/scenarios"
        # Only get scenarios that:
        #   end in .py
        #   don't begin with '__', as __init__.py isn't a scenario but a requirement
        choices = list(x[:-3] for x in os.listdir(scenariodir) if x[-3:] == ".py" and x[:2] != "__")
        # Import the scenarios and store them
        imported_choices = [importlib.import_module("scenarios.%s" % c) for c in choices]
        imported_choices = [c.Import for c in imported_choices if hasattr(c, 'Import')]
        # Check the choices for enabled flag, if not enabled remove them
        filtered_choices = [scenario for scenario in imported_choices
                            if hasattr(scenario, 'enabled')
                            and scenario.enabled]

        # Order choices by their given weights
        def sort_choices(x):
            if hasattr(x, 'weight'):
                return x.weight
            return sys.maxint

        filtered_choices.sort(key=sort_choices)
        # Get the user's chosen scenario
        index = choice_from_list([scenario.name for scenario in filtered_choices], 'scenario')
        chosen_scenario = filtered_choices[index]

        if isStudent:
            # Take in student ID
            seed = raw_input("Enter your ID: ")
            # Create a scenario with ID as seed
            scenario = chosen_scenario(teacher=isTeacher, developer=isDeveloer, seed=seed)
            # Execute scenario
            scenario.run()
            # Reseed the random number generator so the password stays the FTP same between tasks
            random.seed(seed)
            # Host task on FTP
            scenario.run_ftp()

        if isTeacher:
            # Take in student IDs
            seed = raw_input("Enter Student IDs seperated by spaces: ").split(" ")
            # Create and execute scenarios for each ID
            scenario = None
            for s in seed:
                scenario = chosen_scenario(teacher=isTeacher, developer=isDeveloer, seed=s)
                scenario.run()
            # Reseed to a set value
            random.seed("")
            # Host answers for all generated scenarios on ftp
            scenario.run_ftp()

    def cleanup():
        # Clean all docker systems to reduce VM size
        os.system("docker system prune -a --volumes")

    isStudent = False
    isTeacher = False
    isDeveloer = False

    # Use argparse library to parse arguments and print usage/help
    parser = argparse.ArgumentParser()
    parser.add_argument('account',
                        help='The user account to run as (student/teacher).',
                        choices=['student', 'teacher'],
                        nargs='?')  # Sets optional
    args = parser.parse_args()

    if args.account:
        if args.account == 'student':
            isStudent = True
        elif args.account == 'teacher':
            isTeacher = True
    # If no arguments were passed then we're not a student or a teacher
    # give the choice to be any
    else:
        while True:
            choice = raw_input('\n'.join(["[0] student",
                                          "[1] teacher",
                                          "[2] developer",
                                          "Select a user type:"]))
            try:
                choice = int(choice)
            except ValueError:
                # The conversion of choice to int has failed
                print("*** Please enter a valid number.")
                continue
            if choice < 0 or choice > 2:
                # The choice was outside the range
                print("*** Please enter a number in the range 0-2.")
                continue
            # The choice was valid, move on
            break
        if choice == 0:
            isStudent = True
        elif choice == 1:
            isTeacher = True
        elif choice == 2:
            isDeveloer = True

    # Get current directory
    currentdir = os.path.dirname(os.path.realpath(__file__))

    # Create list of options to be presented to the user
    # List contains text to be shown, and function to be executed if chosen
    options = []
    if isDeveloer:
        options.append(("Test All Scenarios", test_scenarios))
        options.append(("Container Examples", containers))
    options.append(("Scenarios", scenarios))
    options.append(("Clean space", cleanup))
    # Print choices
    for i in range(0, len(options)):
        print("[%s] %s" % (i, options[i][0]))
    # Get choice and execute
    options[input("Select a category:")][1]()


if __name__ == "__main__":
    main()
