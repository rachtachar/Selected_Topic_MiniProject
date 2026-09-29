"""
Module: system_process.py
Sourced from Hugging Face: mteb/CodeSearchNetRetrieval
"""
import os
import sys
import re
import json
import time

def bulk_load(self, table, tmp_file):
        """
        
        """
        self.copy_expert("COPY {table} FROM STDIN".format(table=table), tmp_file)

def _wanmen_get_title_by_json_topic_part(json_content, tIndex, pIndex):
    """"""

    return '_'.join([json_content[0]['name'],
                    json_content[0]['Topics'][tIndex]['name'],
                    json_content[0]['Topics'][tIndex]['Parts'][pIndex]['name']])

def _sync_metadata(self):
        """
        
        """
        while not self._stat_queue.empty():
            stat = self._stat_queue.get()
            self._file_paths = stat.file_paths
            self._all_pids = stat.all_pids
            self._done = stat.done
            self._all_files_processed = stat.all_files_processed
            self._result_count += stat.result_count

def chain(*tasks):
    """
    
    """
    for up_task, down_task in zip(tasks[:-1], tasks[1:]):
        up_task.set_downstream(down_task)

def list_versions(self, project_id, model_name):
        """
        
        """
        result = []
        full_parent_name = 'projects/{}/models/{}'.format(
            project_id, model_name)
        request = self._mlengine.projects().models().versions().list(
            parent=full_parent_name, pageSize=100)

        response = request.execute()
        next_page_token = response.get('nextPageToken', None)
        result.extend(response.get('versions', []))
        while next_page_token is not None:
            next_request = self._mlengine.projects().models().versions().list(
                parent=full_parent_name,
                pageToken=next_page_token,
                pageSize=100)
            response = next_request.execute()
            next_page_token = response.get('nextPageToken', None)
            result.extend(response.get('versions', []))
            time.sleep(5)
        return result

def get_uri(self):
        """
        
        """
        conn_config = self._get_conn_params()
        uri = 'snowflake://{user}:{password}@{account}/{database}/'
        uri += '{schema}?warehouse={warehouse}&role={role}'
        return uri.format(**conn_config)

def annotate_text(self, document, features, encoding_type=None, retry=None, timeout=None, metadata=None):
        """
        
        """
        client = self.get_conn()

        return client.annotate_text(
            document=document,
            features=features,
            encoding_type=encoding_type,
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )
