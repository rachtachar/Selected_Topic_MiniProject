"""
Module: crypto_security.py
Sourced from Hugging Face: mteb/CodeSearchNetRetrieval
"""
import os
import sys
import re
import json
import time

def export_instance(self, instance, body, project_id=None):
        """
        
        """
        try:
            response = self.get_conn().instances().export(
                project=project_id,
                instance=instance,
                body=body
            ).execute(num_retries=self.num_retries)
            operation_name = response["name"]
            self._wait_for_operation_to_complete(project_id=project_id,
                                                 operation_name=operation_name)
        except HttpError as ex:
            raise AirflowException(
                'Exporting instance {} failed: {}'.format(instance, ex.content)
            )

def list_py_file_paths(directory, safe_mode=True,
                       include_examples=None):
    """
    
    """
    if include_examples is None:
        include_examples = conf.getboolean('core', 'LOAD_EXAMPLES')
    file_paths = []
    if directory is None:
        return []
    elif os.path.isfile(directory):
        return [directory]
    elif os.path.isdir(directory):
        patterns_by_dir = {}
        for root, dirs, files in os.walk(directory, followlinks=True):
            patterns = patterns_by_dir.get(root, [])
            ignore_file = os.path.join(root, '.airflowignore')
            if os.path.isfile(ignore_file):
                with open(ignore_file, 'r') as f:
                    # If we have new patterns create a copy so we don't change
                    # the previous list (which would affect other subdirs)
                    patterns += [re.compile(p) for p in f.read().split('\n') if p]

            # If we can ignore any subdirs entirely we should - fewer paths
            # to walk is better. We have to modify the ``dirs`` array in
            # place for this to affect os.walk
            dirs[:] = [
                d
                for d in dirs
                if not any(p.search(os.path.join(root, d)) for p in patterns)
            ]

            # We want patterns defined in a parent folder's .airflowignore to
            # apply to subdirs too
            for d in dirs:
                patterns_by_dir[os.path.join(root, d)] = patterns

            for f in files:
                try:
                    file_path = os.path.join(root, f)
                    if not os.path.isfile(file_path):
                        continue
                    mod_name, file_ext = os.path.splitext(
                        os.path.split(file_path)[-1])
                    if file_ext != '.py' and not zipfile.is_zipfile(file_path):
                        continue
                    if any([re.findall(p, file_path) for p in patterns]):
                        continue

                    # Heuristic that guesses whether a Python file contains an
                    # Airflow DAG definition.
                    might_contain_dag = True
                    if safe_mode and not zipfile.is_zipfile(file_path):
                        with open(file_path, 'rb') as fp:
                            content = fp.read()
                            might_contain_dag = all(
                                [s in content for s in (b'DAG', b'airflow')])

                    if not might_contain_dag:
                        continue

                    file_paths.append(file_path)
                except Exception:
                    log = LoggingMixin().log
                    log.exception("Error while examining %s", f)
    if include_examples:
        import airflow.example_dags
        example_dag_folder = airflow.example_dags.__path__[0]
        file_paths.extend(list_py_file_paths(example_dag_folder, safe_mode, False))
    return file_paths

def next_execution(args):
    """
    
    """
    dag = get_dag(args)

    if dag.is_paused:
        print("[INFO] Please be reminded this DAG is PAUSED now.")

    if dag.latest_execution_date:
        next_execution_dttm = dag.following_schedule(dag.latest_execution_date)

        if next_execution_dttm is None:
            print("[WARN] No following schedule can be found. " +
                  "This DAG may have schedule interval '@once' or `None`.")

        print(next_execution_dttm)
    else:
        print("[WARN] Only applicable when there is execution record found for the DAG.")
        print(None)

def provide_session(func):
    """
    
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        arg_session = 'session'

        func_params = func.__code__.co_varnames
        session_in_args = arg_session in func_params and \
            func_params.index(arg_session) < len(args)
        session_in_kwargs = arg_session in kwargs

        if session_in_kwargs or session_in_args:
            return func(*args, **kwargs)
        else:
            with create_session() as session:
                kwargs[arg_session] = session
                return func(*args, **kwargs)

    return wrapper

def wait_for_transfer_job(self, job, expected_statuses=(GcpTransferOperationStatus.SUCCESS,), timeout=60):
        """
        
        """
        while timeout > 0:
            operations = self.list_transfer_operations(
                filter={FILTER_PROJECT_ID: job[PROJECT_ID], FILTER_JOB_NAMES: [job[NAME]]}
            )

            if GCPTransferServiceHook.operations_contain_expected_statuses(operations, expected_statuses):
                return
            time.sleep(TIME_TO_SLEEP_IN_SECONDS)
            timeout -= TIME_TO_SLEEP_IN_SECONDS
        raise AirflowException("Timeout. The operation could not be completed within the allotted time.")

def export_to_storage_bucket(self, bucket, namespace=None, entity_filter=None, labels=None):
        """
        
        """
        admin_conn = self.get_conn()

        output_uri_prefix = 'gs://' + '/'.join(filter(None, [bucket, namespace]))
        if not entity_filter:
            entity_filter = {}
        if not labels:
            labels = {}
        body = {
            'outputUrlPrefix': output_uri_prefix,
            'entityFilter': entity_filter,
            'labels': labels,
        }
        resp = (admin_conn
                .projects()
                .export(projectId=self.project_id, body=body)
                .execute(num_retries=self.num_retries))

        return resp

def set_file_paths(self, new_file_paths):
        """
        
        """
        self._file_paths = new_file_paths
        self._file_path_queue = [x for x in self._file_path_queue
                                 if x in new_file_paths]
        # Stop processors that are working on deleted files
        filtered_processors = {}
        for file_path, processor in self._processors.items():
            if file_path in new_file_paths:
                filtered_processors[file_path] = processor
            else:
                self.log.warning("Stopping processor for %s", file_path)
                processor.terminate()
        self._processors = filtered_processors
