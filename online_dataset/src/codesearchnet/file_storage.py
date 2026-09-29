"""
Module: file_storage.py
Sourced from Hugging Face: mteb/CodeSearchNetRetrieval
"""
import os
import sys
import re
import json
import time

def get_video_url_from_video_id(video_id):
    """"""
    # from js
    data = [""] * 256
    for index, _ in enumerate(data):
        t = index
        for i in range(8):
            t = -306674912 ^ unsigned_right_shitf(t, 1) if 1 & t else unsigned_right_shitf(t, 1)
        data[index] = t

    def tmp():
        rand_num = random.random()
        path = "/video/urls/v/1/toutiao/mp4/{video_id}?r={random_num}".format(video_id=video_id,
                                                                              random_num=str(rand_num)[2:])
        e = o = r = -1
        i, a = 0, len(path)
        while i < a:
            e = ord(path[i])
            i += 1
            if e < 128:
                r = unsigned_right_shitf(r, 8) ^ data[255 & (r ^ e)]
            else:
                if e < 2048:
                    r = unsigned_right_shitf(r, 8) ^ data[255 & (r ^ (192 | e >> 6 & 31))]
                    r = unsigned_right_shitf(r, 8) ^ data[255 & (r ^ (128 | 63 & e))]
                else:
                    if 55296 <= e < 57344:
                        e = (1023 & e) + 64
                        i += 1
                        o = 1023 & t.url(i)
                        r = unsigned_right_shitf(r, 8) ^ data[255 & (r ^ (240 | e >> 8 & 7))]
                        r = unsigned_right_shitf(r, 8) ^ data[255 & (r ^ (128 | e >> 2 & 63))]
                        r = unsigned_right_shitf(r, 8) ^ data[255 & (r ^ (128 | o >> 6 & 15 | (3 & e) << 4))]
                        r = unsigned_right_shitf(r, 8) ^ data[255 & (r ^ (128 | 63 & o))]
                    else:
                        r = unsigned_right_shitf(r, 8) ^ data[255 & (r ^ (224 | e >> 12 & 15))]
                        r = unsigned_right_shitf(r, 8) ^ data[255 & (r ^ (128 | e >> 6 & 63))]
                        r = unsigned_right_shitf(r, 8) ^ data[255 & (r ^ (128 | 63 & e))]

        return "https://ib.365yg.com{path}&s={param}".format(path=path, param=unsigned_right_shitf(r ^ -1, 0))

    while 1:
        url = tmp()
        if url.split("=")[-1][0] != "-":  # 参数s不能为负数
            return url

def get_document(self, document_id, database_name=None, collection_name=None):
        """
        
        """
        if document_id is None:
            raise AirflowBadRequest("Cannot get a document without an id")

        try:
            return self.get_conn().ReadItem(
                get_document_link(
                    self.__get_database_name(database_name),
                    self.__get_collection_name(collection_name),
                    document_id))
        except HTTPFailure:
            return None

def make_aware(value, timezone=None):
    """
    

    """
    if timezone is None:
        timezone = TIMEZONE

    # Check that we won't overwrite the timezone of an aware datetime.
    if is_localized(value):
        raise ValueError(
            "make_aware expects a naive datetime, got %s" % value)
    if hasattr(value, 'fold'):
        # In case of python 3.6 we want to do the same that pendulum does for python3.5
        # i.e in case we move clock back we want to schedule the run at the time of the second
        # instance of the same clock time rather than the first one.
        # Fold parameter has no impact in other cases so we can safely set it to 1 here
        value = value.replace(fold=1)
    if hasattr(timezone, 'localize'):
        # This method is available for pytz time zones.
        return timezone.localize(value)
    elif hasattr(timezone, 'convert'):
        # For pendulum
        return timezone.convert(value)
    else:
        # This may be wrong around DST changes!
        return value.replace(tzinfo=timezone)

def allocate_ids(self, partial_keys):
        """
        
        """
        conn = self.get_conn()

        resp = (conn
                .projects()
                .allocateIds(projectId=self.project_id, body={'keys': partial_keys})
                .execute(num_retries=self.num_retries))

        return resp['keys']

def fetch_celery_task_state(celery_task):
    """
    
    """

    try:
        with timeout(seconds=2):
            # Accessing state property of celery task will make actual network request
            # to get the current state of the task.
            res = (celery_task[0], celery_task[1].state)
    except Exception as e:
        exception_traceback = "Celery Task ID: {}\n{}".format(celery_task[0],
                                                              traceback.format_exc())
        res = ExceptionWithTraceback(e, exception_traceback)
    return res

def get_conn(self):
        """
        
        """

        self.log.debug('Creating SSH client for conn_id: %s', self.ssh_conn_id)
        client = paramiko.SSHClient()
        if not self.allow_host_key_change:
            self.log.warning('Remote Identification Change is not verified. '
                             'This wont protect against Man-In-The-Middle attacks')
            client.load_system_host_keys()
        if self.no_host_key_check:
            self.log.warning('No Host Key Verification. This wont protect '
                             'against Man-In-The-Middle attacks')
            # Default is RejectPolicy
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if self.password and self.password.strip():
            client.connect(hostname=self.remote_host,
                           username=self.username,
                           password=self.password,
                           key_filename=self.key_file,
                           timeout=self.timeout,
                           compress=self.compress,
                           port=self.port,
                           sock=self.host_proxy)
        else:
            client.connect(hostname=self.remote_host,
                           username=self.username,
                           key_filename=self.key_file,
                           timeout=self.timeout,
                           compress=self.compress,
                           port=self.port,
                           sock=self.host_proxy)

        if self.keepalive_interval:
            client.get_transport().set_keepalive(self.keepalive_interval)

        self.client = client
        return client

def get_dag(self, dag_id):
        """
        
        """
        from airflow.models.dag import DagModel  # Avoid circular import

        # If asking for a known subdag, we want to refresh the parent
        root_dag_id = dag_id
        if dag_id in self.dags:
            dag = self.dags[dag_id]
            if dag.is_subdag:
                root_dag_id = dag.parent_dag.dag_id

        # If the dag corresponding to root_dag_id is absent or expired
        orm_dag = DagModel.get_current(root_dag_id)
        if orm_dag and (
                root_dag_id not in self.dags or
                (
                    orm_dag.last_expired and
                    dag.last_loaded < orm_dag.last_expired
                )
        ):
            # Reprocess source file
            found_dags = self.process_file(
                filepath=orm_dag.fileloc, only_if_updated=False)

            # If the source file no longer exports `dag_id`, delete it from self.dags
            if found_dags and dag_id in [found_dag.dag_id for found_dag in found_dags]:
                return self.dags[dag_id]
            elif dag_id in self.dags:
                del self.dags[dag_id]
        return self.dags.get(dag_id)

def create_job(self, project_id, job, use_existing_job_fn=None):
        """
        
        """
        request = self._mlengine.projects().jobs().create(
            parent='projects/{}'.format(project_id),
            body=job)
        job_id = job['jobId']

        try:
            request.execute()
        except HttpError as e:
            # 409 means there is an existing job with the same job ID.
            if e.resp.status == 409:
                if use_existing_job_fn is not None:
                    existing_job = self._get_job(project_id, job_id)
                    if not use_existing_job_fn(existing_job):
                        self.log.error(
                            'Job with job_id %s already exist, but it does '
                            'not match our expectation: %s',
                            job_id, existing_job
                        )
                        raise
                self.log.info(
                    'Job with job_id %s already exist. Will waiting for it to finish',
                    job_id
                )
            else:
                self.log.error('Failed to create MLEngine job: {}'.format(e))
                raise

        return self._wait_for_job_done(project_id, job_id)
