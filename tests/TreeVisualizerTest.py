
import unittest
import shutil
import os

import networkx as nx

from data_allocator.tree_visualizer import TreeVisualizer
from data_allocator.storage_manager import StorageManager
from unittest.mock import MagicMock

class TestTreeVisualizer(unittest.TestCase):

    def setUp(self):
        self.test_path = "wdir/test_tree_visualizer"
        os.makedirs(self.test_path, exist_ok=True)

        self.storage = StorageManager(db_path=os.path.join(self.test_path, "test.db"))

        self.visualizer = TreeVisualizer(storage_manager=self.storage)
        self.storage.record_location("ProjectA/SubA1", "drive1")
        self.storage.record_location("ProjectA/SubA2", "drive1")
        self.storage.record_location("ProjectB/SubB1", "drive2")
        self.storage.record_location("ProjectB/SubB2", "drive2")
        self.storage.record_location("ProjectB/SubB1/Sub.1", "drive1")
        self.storage.record_location("ProjectB/SubB2/Sub.1", "drive2")

    def tearDown(self):
        shutil.rmtree(self.test_path)
        return super().tearDown()

    def test_build_tree(self):
        """Test that the tree builds correctly."""
        tree = self.visualizer.build_tree()

        # Parent-child relationships
        self.assertTrue(tree.has_edge("ProjectA", "ProjectA/SubA1"))
        self.assertTrue(tree.has_edge("ProjectA", "ProjectA/SubA2"))
        self.assertTrue(tree.has_edge("ProjectB", "ProjectB/SubB1"))
        self.assertTrue(tree.has_edge("ProjectB", "ProjectB/SubB2"))

        tree = self.visualizer.build_tree(root_branch="ProjectB")
        self.assertTrue(tree.has_edge("ProjectB", "ProjectB/SubB1"))
        self.assertTrue(tree.has_edge("ProjectB", "ProjectB/SubB2"))
        self.assertTrue(tree.has_edge("ProjectB/SubB1", "ProjectB/SubB1/Sub.1"))
        self.assertFalse(tree.has_edge("ProjectA", "ProjectA/SubA1"))

    def test_tree_structure(self):
        """Test that tree2str() returns the correct string representation."""
        tree = self.visualizer.build_tree()
        tree_str = self.visualizer.tree2str(tree)

        expected_output = "    ProjectA\n" \
            "        ProjectA/SubA1\n" \
            "        ProjectA/SubA2\n" \
            "    ProjectB\n" \
            "        ProjectB/SubB1\n" \
            "            ProjectB/SubB1/Sub.1\n" \
            "        ProjectB/SubB2\n" \
            "            ProjectB/SubB2/Sub.1\n"

        self.assertEqual(tree_str.strip(), expected_output.strip())

        # test with different root
        tree = self.visualizer.build_tree(root_branch="ProjectB/SubB1")
        expected_output = "ProjectB/SubB1\n" \
                          "    ProjectB/SubB1/Sub.1\n"
        self.assertEqual(self.visualizer.tree2str(tree).strip(), expected_output.strip())

    def test_multiple_roots_exception(self):
        """Test that trees with multiple roots raise an exception."""
        tree = nx.DiGraph()
        tree.add_edges_from([
            ("Root1", "Child1"),
            ("Root2", "Child2")  # Multiple roots exist
        ])

        with self.assertRaises(Exception) as context:
            self.visualizer.tree2str(tree)

        self.assertIn("Tree has multiple roots", str(context.exception))

if __name__ == "__main__":
    unittest.main()
