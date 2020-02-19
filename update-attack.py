import argparse
import colorama
import json
import os
import time
from string import Template

import modules
from modules import site_config
from modules import util

# argument defaults and options for the CLI
module_choices = ['clean', 'stix_data', 'resources', 'contribute', 'groups', 'search', 'matrices', 'mitigations', 'redirects', 'software', 'tactics', 'techniques', "prev_versions", "website_build", "tests"]
test_choices = ['size', 'links', 'external_links', 'citations']

def get_parsed_args():
    """Create argument parser and parse arguments"""

    parser = argparse.ArgumentParser(description=("Build the ATT&CK website.\n"
                                     "To run a complete build, run this script with the -c and -b flags. "))
    parser.add_argument('--refresh', '-r', action='store_true',
                        help='Pull down the current STIX data from the MITRE/CTI GitHub respository')
    parser.add_argument('--no-stix-link-replacement', action='store_true',
                        help="If this flag is absent, links to attack.mitre.org/[page] in the STIX data will be replaced with /[page]. Add this flag to preserve links to attack.mitre.org.")
    
    parser.add_argument('--modules', '-m', nargs='*',
                        type=str,
                        choices=module_choices,
                        help=("Run modules. If no option is specified, "
                              "it will run all modules from the modules directory. "
                              "Run specific modules by selecting from the "
                              "list and leaving one space in "
                              "between them. For example: '-m clean techniques tactics'."))                          
    parser.add_argument('--test', '-t', nargs='*',
                        choices=test_choices,
                        dest="tests",
                        help="Run tests. If no option is specified, "
                              "all choices will be selected except external_links. "
                              "Run specific tests "
                              "by selecting from the list and leaving "
                              "one space in between them. For example: '-t output links'. "
                              "Tests: "
                              "size (size of output directory against github pages limit); "
                              "links (dead internal hyperlinks and relative hyperlinks); "
                              "external_links (dead external hyperlinks); "
                              "citations (unparsed citation text).")
    
    parser.add_argument('--proxy', help="set proxy")

    parser.add_argument("--print-tests", 
                        dest="print_tests", 
                        action="store_true",
                        help="Force test output to print to stdout even if the results are very long.")

    parser.add_argument("--no-test-exitstatus", 
                        dest="override_exit_status", 
                        action='store_true', 
                        help="Forces application to exit with success status codes even if tests fail.")

    args = parser.parse_args()

    # Set global argument list for modules
    site_config.args = args
    
    return args

def remove_from_build(arg_modules):
    """ Given a list of modules from command line, remove modules that appear in module
        directory that are not in list.
    """

    def remove_from_running_pool():
        """ Remove modules from running pool if they are not in modules list from argument """

        copy_of_modules = [] 

        for module in modules.run_ptr:
            if module["name"].lower() in arg_modules:
                copy_of_modules.append(module)
        
        modules.run_ptr = copy_of_modules
        
    def remove_from_menu():
        """ Remove modules from menu if they are not in modules list from argument """

        for module in modules.menu_ptr:
            if module["name"].lower() not in arg_modules:
                modules.menu_ptr.remove(module)
    
    remove_from_running_pool()
    remove_from_menu()

if __name__ == "__main__":
    """Beginning of ATT&CK update module"""

    # Get args
    args = get_parsed_args()

    # If modules flags are called only run modules selected by user
    if args.modules:
        remove_from_build(args.modules)

    # Start time of update
    update_start = time.time()

    # Init colorama for output
    colorama.init()

    # Get running modules and priorities
    for ptr in modules.run_ptr:
        util.buildhelpers.print_start(ptr['name'])
        start_time = time.time()
        ptr['run_module']()
        end_time = time.time()
        util.buildhelpers.print_end(ptr['name'], start_time, end_time)

    # Print end of module
    update_end = time.time()
    util.buildhelpers.print_end("TOTAL Update Time", update_start, update_end)