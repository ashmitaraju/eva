# coding=utf-8
# Copyright 2018-2022 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import unittest
from test.util import file_remove, load_inbuilt_udfs

import numpy as np

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager
from eva.configuration.constants import EVA_ROOT_DIR
from eva.server.command_handler import execute_query_fetch_all


class DeleteExecutorTest(unittest.TestCase):
    def setUp(self):
        # Bootstrap configuration manager.
        ConfigurationManager()

        # Reset catalog.
        CatalogManager().reset()

        load_inbuilt_udfs()

        create_table_query = """
                CREATE TABLE IF NOT EXISTS testDeleteOne
                (
                 id INTEGER,
                 feat   NDARRAY FLOAT32(1, 3),
                 input  NDARRAY UINT8(1, 3)
                 );
                """
        execute_query_fetch_all(create_table_query)

        insert_query1 = """
                INSERT INTO testDeleteOne (id, feat, input)
                VALUES (5, [[0, 0, 0]], [[0, 0, 0]]);
        """
        execute_query_fetch_all(insert_query1)
        insert_query2 = """
                INSERT INTO testDeleteOne (id, feat, input)
                VALUES (15, [[100, 100, 100]], [[100, 100, 100]]);
        """
        execute_query_fetch_all(insert_query2)
        insert_query3 = """
                INSERT INTO testDeleteOne (id, feat, input)
                VALUES (25, [[200, 200, 200]], [[200, 200, 200]]);
        """
        execute_query_fetch_all(insert_query3)

        ####################################################
        # Create a table for testing Delete with Video Data#
        ####################################################

        path = f"{EVA_ROOT_DIR}/data/sample_videos/1/*.mp4"
        query = f'LOAD VIDEO "{path}" INTO TestDeleteVideos;'
        _ = execute_query_fetch_all(query)

    def tearDown(self):
        file_remove("dummy.avi")

    # integration test
    @unittest.skip("Not supported in current version")
    def test_should_delete_single_video_in_table(self):
        path = f"{EVA_ROOT_DIR}/data/sample_videos/1/2.mp4"
        delete_query = f"""DELETE FROM TestDeleteVideos WHERE name="{path}";"""
        batch = execute_query_fetch_all(delete_query)

        query = "SELECT name FROM MyVideo"
        batch = execute_query_fetch_all(query)
        self.assertIsNone(
            np.testing.assert_array_equal(
                batch.frames["data"][0],
                np.array([[[40, 40, 40], [40, 40, 40]], [[40, 40, 40], [40, 40, 40]]]),
            )
        )

        query = "SELECT id, data FROM MyVideo WHERE id = 41;"
        batch = execute_query_fetch_all(query)
        self.assertIsNone(
            np.testing.assert_array_equal(
                batch.frames["data"][0],
                np.array([[[41, 41, 41], [41, 41, 41]], [[41, 41, 41], [41, 41, 41]]]),
            )
        )

    @unittest.skip("Not supported in current version")
    def test_should_delete_single_image_in_table(self):
        path = f"{EVA_ROOT_DIR}/data/sample_videos/1/2.mp4"
        delete_query = f"""DELETE FROM TestDeleteVideos WHERE name="{path}";"""
        batch = execute_query_fetch_all(delete_query)

        query = "SELECT name FROM MyVideo"
        batch = execute_query_fetch_all(query)
        self.assertIsNone(
            np.testing.assert_array_equal(
                batch.frames["data"][0],
                np.array([[[40, 40, 40], [40, 40, 40]], [[40, 40, 40], [40, 40, 40]]]),
            )
        )

        query = "SELECT id, data FROM MyVideo WHERE id = 41;"
        batch = execute_query_fetch_all(query)
        self.assertIsNone(
            np.testing.assert_array_equal(
                batch.frames["data"][0],
                np.array([[[41, 41, 41], [41, 41, 41]], [[41, 41, 41], [41, 41, 41]]]),
            )
        )

    def test_should_delete_tuple_in_table(self):
        delete_query = "DELETE FROM testDeleteOne WHERE id < 20;"
        batch = execute_query_fetch_all(delete_query)

        query = "SELECT * FROM testDeleteOne;"
        batch = execute_query_fetch_all(query)
        from eva.utils.logging_manager import logger

        logger.info(batch)
        np.testing.assert_array_equal(
            batch.frames["testdeleteone.id"].array,
            np.array([25], dtype=np.int64),
        )
