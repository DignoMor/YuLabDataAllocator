# data_allocator/tree_visualizer.py

import os

import networkx as nx

from collections import deque
from data_allocator.storage_manager import StorageManager

class TreeVisualizer:
    def __init__(self, storage_manager):
        """
        Initialize the TreeVisualizer with StorageManager.
        """
        self.storage = storage_manager

    def build_tree(self, root_branch=None):
        """
        Build the tree structure using NetworkX DiGraph.

        Keyword arguments:
        - root_branch: The root branch to start building the tree from.

        Returns:
        - tree: A NetworkX DiGraph representing the tree structure.
        """
        tree = nx.DiGraph()
        all_branches = self.storage.get_all_locations2drive()

        if not root_branch:
            root_branch = ""
            branches2plot = list(all_branches.keys())
        else:
            branches2plot = [b for b in all_branches.keys() if b.startswith(root_branch) and (b != root_branch)] 

        # sort the branches by length so that the parent nodes are added first
        branches2plot.sort(key=len)

        # build the tree
        tree.add_node(root_branch)
        for branch in branches2plot:
            all_nodes = branch.replace(root_branch, "").lstrip("/").split("/")
            if root_branch == "":
                all_nodes_full_path = ["/".join(all_nodes[:i+1]) for i in range(len(all_nodes))]
            else:
                all_nodes_full_path = [root_branch + "/" + "/".join(all_nodes[:i+1]) for i in range(len(all_nodes))]

            tree.add_edge(root_branch, all_nodes_full_path[0])
            for i in range(0, len(all_nodes)-1):
                parent = all_nodes_full_path[i]
                child = all_nodes_full_path[i+1]

                if not tree.has_edge(parent, child):
                    tree.add_edge(parent, child)

        return tree

    @staticmethod
    def get_subtree(graph, root):
        """
        Extracts a subtree rooted at `root` and returns it as a new DiGraph.

        Parameters:
        - graph (nx.DiGraph): The original directed tree.
        - root (str): The root node of the desired subtree.

        Returns:
        - subtree (nx.DiGraph): The extracted subtree as a new graph.
        """
        descendants = nx.descendants(graph, root)  # Get all descendants
        subtree_nodes = {root} | descendants  # Include the root itself
        
        # Extract edges where both nodes are in the subtree
        subtree_edges = [(u, v) for u, v in graph.edges if (u in subtree_nodes) and (v in subtree_nodes)]

        # Create new DiGraph for the subtree
        subtree = nx.DiGraph()
        subtree.add_nodes_from(subtree_nodes)
        subtree.add_edges_from(subtree_edges)

        return subtree

    @staticmethod
    def tree2str(tree, indent_level=0, short_tree=False):
        """
        String representation of a DiGraph tree.
        """
        indent="    " * indent_level
        root_nodes = [node for node in tree.nodes if tree.in_degree(node) == 0]

        if not len(root_nodes) == 1:
            raise Exception("Tree has multiple roots")
        
        root_node = root_nodes[0]

        child = list(tree.successors(root_node))
        output_str = indent + "{}\n".format(os.path.basename(root_node) if short_tree else root_node)

        for c in child:
            sub_tree = TreeVisualizer.get_subtree(tree, c)
            output_str += TreeVisualizer.tree2str(sub_tree, 
                                                  indent_level=indent_level+1, 
                                                  short_tree=short_tree, 
                                                  )

        return output_str
