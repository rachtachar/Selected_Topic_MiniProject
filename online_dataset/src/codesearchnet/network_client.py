"""
Module: network_client.py
Sourced from Hugging Face: mteb/CodeSearchNetRetrieval
"""
import os
import sys
import re
import json
import time

def sina_download_by_vid(vid, title=None, output_dir='.', merge=True, info_only=False):
    """
    """
    xml = api_req(vid)
    urls, name, size = video_info(xml)
    if urls is None:
        log.wtf(name)
    title = name
    print_info(site_info, title, 'flv', size)
    if not info_only:
        download_urls(urls, title, 'flv', size, output_dir = output_dir, merge = merge)

def upsert_document(self, document, database_name=None, collection_name=None, document_id=None):
        """
        
        """
        # Assign unique ID if one isn't provided
        if document_id is None:
            document_id = str(uuid.uuid4())

        if document is None:
            raise AirflowBadRequest("You cannot insert a None document")

        # Add document id if isn't found
        if 'id' in document:
            if document['id'] is None:
                document['id'] = document_id
        else:
            document['id'] = document_id

        created_document = self.get_conn().CreateItem(
            get_collection_link(
                self.__get_database_name(database_name),
                self.__get_collection_name(collection_name)),
            document)

        return created_document

def task_failed_deps(args):
    """
    
    """
    dag = get_dag(args)
    task = dag.get_task(task_id=args.task_id)
    ti = TaskInstance(task, args.execution_date)

    dep_context = DepContext(deps=SCHEDULER_DEPS)
    failed_deps = list(ti.get_failed_dep_statuses(dep_context=dep_context))
    # TODO, Do we want to print or log this
    if failed_deps:
        print("Task instance dependencies not met:")
        for dep in failed_deps:
            print("{}: {}".format(dep.dep_name, dep.reason))
    else:
        print("Task instance dependencies are all met.")

def patch_database(self, instance, database, body, project_id=None):
        """
        
        """
        response = self.get_conn().databases().patch(
            project=project_id,
            instance=instance,
            database=database,
            body=body
        ).execute(num_retries=self.num_retries)
        operation_name = response["name"]
        self._wait_for_operation_to_complete(project_id=project_id,
                                             operation_name=operation_name)

def start(self):
        """
        
        """

        self.log.info("Processing files using up to %s processes at a time ", self._parallelism)
        self.log.info("Process each file at most once every %s seconds", self._file_process_interval)
        self.log.info(
            "Checking for new files in %s every %s seconds", self._dag_directory, self.dag_dir_list_interval
        )

        if self._async_mode:
            self.log.debug("Starting DagFileProcessorManager in async mode")
            self.start_in_async()
        else:
            self.log.debug("Starting DagFileProcessorManager in sync mode")
            self.start_in_sync()

def start(self):
        """
        
        """
        self._process = self._launch_process(self._dag_directory,
                                             self._file_paths,
                                             self._max_runs,
                                             self._processor_factory,
                                             self._child_signal_conn,
                                             self._stat_queue,
                                             self._result_queue,
                                             self._async_mode)
        self.log.info("Launched DagFileProcessorManager with pid: %s", self._process.pid)

def refresh_from_db(self, session=None):
        """
        
        """
        DR = DagRun

        exec_date = func.cast(self.execution_date, DateTime)

        dr = session.query(DR).filter(
            DR.dag_id == self.dag_id,
            func.cast(DR.execution_date, DateTime) == exec_date,
            DR.run_id == self.run_id
        ).one()

        self.id = dr.id
        self.state = dr.state

def end(self):
        """
        
        """
        if not self._process:
            self.log.warn('Ending without manager process.')
            return
        this_process = psutil.Process(os.getpid())
        try:
            manager_process = psutil.Process(self._process.pid)
        except psutil.NoSuchProcess:
            self.log.info("Manager process not running.")
            return

        # First try SIGTERM
        if manager_process.is_running() \
                and manager_process.pid in [x.pid for x in this_process.children()]:
            self.log.info("Terminating manager process: %s", manager_process.pid)
            manager_process.terminate()
            # TODO: Remove magic number
            timeout = 5
            self.log.info("Waiting up to %ss for manager process to exit...", timeout)
            try:
                psutil.wait_procs({manager_process}, timeout)
            except psutil.TimeoutExpired:
                self.log.debug("Ran out of time while waiting for "
                               "processes to exit")

        # Then SIGKILL
        if manager_process.is_running() \
                and manager_process.pid in [x.pid for x in this_process.children()]:
            self.log.info("Killing manager process: %s", manager_process.pid)
            manager_process.kill()
            manager_process.wait()
