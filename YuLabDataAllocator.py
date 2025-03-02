#!/usr/bin/env python3

import argparse
import sys
import os

from data_allocator.allocator import Allocator
from data_allocator.storage_manager import StorageManager
from data_allocator.tree_visualizer import TreeVisualizer

CONFIG_PATH=os.path.join(os.environ.get("HOME"), ".YuLabDataAllocator", "config.json")
DB_PATH=os.path.join(os.environ.get("HOME"), ".YuLabDataAllocator", "YuLabDataAllocator.db")

def allocate_branch(branch_name):
    """
    Allocate a new branch.
    """
    allocator = Allocator(config_path=CONFIG_PATH, 
                          db_path=DB_PATH, 
                          )

    try:
        path = allocator.allocate(branch_name)
        sys.stdout.write(path + "\n")
    except Exception as e:
        raise e

def get_branch_path(branch_name):
    """
    Get the full path of an existing branch.
    """
    allocator = Allocator(config_path=CONFIG_PATH, 
                          db_path=DB_PATH, 
                          )
    try:
        path = allocator.get_path(branch_name)
        sys.stdout.write(path + "\n")
    except Exception as e:
        raise e

def delete_branch(branch_name):
    """
    Delete a branch and its record.
    """
    allocator = Allocator(config_path=CONFIG_PATH, 
                          db_path=DB_PATH, 
                          )
    try:
        allocator.delete_branch(branch_name)
    except Exception as e:
        raise e

def ls_root(root): 
    visualizer = TreeVisualizer(storage_manager=StorageManager(db_path=DB_PATH))
    tree = visualizer.build_tree(root_branch=root)
    output_str = TreeVisualizer.tree2str(tree)

    sys.stdout.write(output_str)

def main():
    """
    Main function to parse arguments and call the appropriate function.
    """
    parser = argparse.ArgumentParser(
        description="Yulab Data Allocator: Manage data allocation across multiple drives."
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Allocate Command
    allocate_parser = subparsers.add_parser("allocate", help="Allocate a new branch")
    allocate_parser.add_argument("branch_name", type=str, help="Name of the branch to allocate")

    # Get Path Command
    get_parser = subparsers.add_parser("get", help="Get the path of an existing branch")
    get_parser.add_argument("branch_name", type=str, help="Name of the branch to get the path")

    # Delete Command
    delete_parser = subparsers.add_parser("delete", help="Delete a branch and its record")
    delete_parser.add_argument("branch_name", type=str, help="Name of the branch to delete")

    # ls command
    ls_parser = subparsers.add_parser("ls", help="List all branches")
    ls_parser.add_argument("--root", 
                           type=str, 
                           help="Root branch to list", 
                           default="", 
                           )

    # Parse arguments
    args = parser.parse_args()

    # Handle commands
    if args.command == "allocate":
        allocate_branch(args.branch_name)
    elif args.command == "get":
        get_branch_path(args.branch_name)
    elif args.command == "delete":
        delete_branch(args.branch_name)
    elif args.command == "ls":
        ls_root(args.root)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
