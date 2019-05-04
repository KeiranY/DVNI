"""
Start Function
==============


This module is run upon login from a student or teacher account.
It allows the user to select the scenario they are taking part in and provides them with instructions.

"""

import os
import importlib
import argparse
import sys

import random

from mininet.log import setLogLevel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Type
    from scenarios import Scenario


def _choice_from_list(l, name='item'):
    """
    Helper Function.
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


def get_args():
    """
    Checks command line arguments to see if we're a student, teacher, or developer.

    Example:
        >>> sys.argv[1] = 'teacher'
        >>> get_args()['teacher']
        True
        >>> get_args()['developer']
        False

    :rtype: Dict
    :return: Returns a dictionary with the current directory, our teacher status, and our student status.
    """
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
        # If were running as teacher, store it
        if args.account == 'teacher':
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
        if choice == 1:
            isTeacher = True
        elif choice == 2:
            isDeveloer = True

    return {
        'directory': os.path.dirname(os.path.realpath(__file__)),  # Get current directory
        'teacher': isTeacher,
        'developer': isDeveloer
    }


def containers(args):
    """
    Allows running the 'example' function in each container for testing purposes

    :param args: Arguments from the 'get_args' function in this module.

    TODO
        Add filter for containers that contain an 'example' function, currently choosing a container without one would cause an uncaught error. [Priority=low]
    """
    # Get every container in the container folder
    containerdir = args['directory'] + "/container"
    choices = list(x for x in os.listdir(containerdir) if not os.path.isfile(os.path.join(containerdir, x)))
    # Get the user's chosen container
    index = _choice_from_list(choices, 'container')
    # Import and run the container example
    importlib.import_module("container.%s.example" % choices[index])


def get_scenarios(directory):
    # type: (str) -> List[Type[Scenario]]
    """
    Gets a list of enabled scenarios in the given directory and returns them.
    Scenarios are listed by their 'weight', a value defined in their class used for ordering.

    Example:
        >>> print(get_scenarios('/vagrant/scenarios/')[0].name)
        Host Scanning

    :param directory: Directory to look for scenarios in, usually '$ProjectRoot/scenarios/'
    :return: List[Scenario]
    """
    # Only get scenarios that:
    #   end in .py
    #   don't begin with '__', these for are internal usage such as __init__
    choices = list(x[:-3] for x in os.listdir(directory) if x[-3:] == ".py" and x[:2] != "__")
    # Import the scenarios and store them
    choices = [importlib.import_module("scenarios.%s" % c) for c in choices]
    # Only include the scenarios that have an 'Import' class
    choices = [c.Import for c in choices if hasattr(c, 'Import')]
    # Check the choices for enabled flag, if not enabled remove them
    choices = [scenario for scenario in choices
               if hasattr(scenario, 'enabled')
               and scenario.enabled]

    # Order choices by their given weights
    choices.sort(key=lambda x: x.weight if hasattr(x, 'weight') else sys.maxint)
    return choices


def test_scenarios(args):
    """
    Runs every enables scenario with the seed 1-5 for testing purposes

    :param args: Arguments from the 'get_args' function in this module.

    TODO
         Could generate random seeds for this? [Priority=low]
    """
    choices = get_scenarios(args['directory'] + "/scenarios")
    setLogLevel("error")
    for seed in range(5):
        for scenario in choices:
            print('*** %s SEED:%s' % (scenario.name, str(seed)))
            scenario(teacher=True, seed=str(seed)).run()


def run_scenario(args):
    """
    Allows a student to select a single scenario to take part in.

    :param args: Arguments from the 'get_args' function in this module.
    """
    # Get scenario list
    choices = get_scenarios(args['directory'] + "/scenarios")
    # Get the user's chosen scenario
    index = _choice_from_list([scenario.name for scenario in choices], 'scenario')
    chosen_scenario = choices[index]

    # Take in student ID
    seed = raw_input("Enter your ID: ")
    # Create a scenario with ID as seed
    scenario = chosen_scenario(teacher=False, developer=args['developer'], seed=seed)
    # Execute scenario
    scenario.run()
    # Reseed the random number generator so the password stays the FTP same between tasks
    random.seed(seed)
    # Host task on FTP
    scenario.run_ftp()


def batch_scenario(args):
    """
    Allows a teacher to select a scenario with several student IDs at a time.

    :param args: Arguments from the 'get_args' function in this module.
    """
    # Get scenario list
    choices = get_scenarios(args['directory'] + "/scenarios")
    # Get the user's chosen scenario
    index = _choice_from_list([scenario.name for scenario in choices], 'scenario')
    chosen_scenario = choices[index]

    # Take in student IDs
    seed = raw_input("Enter Student IDs seperated by spaces: ").split(" ")
    # Create and execute scenarios for each ID
    scenario = None
    for s in seed:
        scenario = chosen_scenario(teacher=True, developer=args['developer'], seed=s)
        scenario.run()
    # Reseed to a set value
    random.seed("")
    # Host answers for all generated scenarios on ftp
    scenario.run_ftp()


def cleanup():
    """
        Clean all docker systems to reduce VM size
    """
    os.system("docker system prune -a --volumes")


def main():
    """Run if we're the main file"""

    args = get_args()
    # Create list of options to be presented to the user
    # List contains text to be shown, and function to be executed if chosen
    options = []
    # Give testing options to devs
    if args['developer']:
        options.append(("Test All Scenarios", test_scenarios))
        options.append(("Container Examples", containers))
    # Give single task options to students
    if not args['teacher']:
        options.append(("Scenarios", run_scenario))
    # Give batch task options to teachers
    else:
        options.append(("Scenarios", batch_scenario))
    options.append(("Clean space", cleanup))
    # Print choices
    for i in range(0, len(options)):
        print("[%s] %s" % (i, options[i][0]))
    # Get choice and execute
    options[input("Select a category:")][1](args)


if __name__ == "__main__":
    main()