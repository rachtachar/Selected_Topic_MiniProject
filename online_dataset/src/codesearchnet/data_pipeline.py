"""
Module: data_pipeline.py
Sourced from Hugging Face: mteb/CodeSearchNetRetrieval
"""
import os
import sys
import re
import json
import time

def post_content(url, headers={}, post_data={}, decoded=True, **kwargs):
    """
    """
    if kwargs.get('post_data_raw'):
        logging.debug('post_content: %s\npost_data_raw: %s' % (url, kwargs['post_data_raw']))
    else:
        logging.debug('post_content: %s\npost_data: %s' % (url, post_data))

    req = request.Request(url, headers=headers)
    if cookies:
        cookies.add_cookie_header(req)
        req.headers.update(req.unredirected_hdrs)
    if kwargs.get('post_data_raw'):
        post_data_enc = bytes(kwargs['post_data_raw'], 'utf-8')
    else:
        post_data_enc = bytes(parse.urlencode(post_data), 'utf-8')
    response = urlopen_with_retry(req, data=post_data_enc)
    data = response.read()

    # Handle HTTP compression for gzip and deflate (zlib)
    content_encoding = response.getheader('Content-Encoding')
    if content_encoding == 'gzip':
        data = ungzip(data)
    elif content_encoding == 'deflate':
        data = undeflate(data)

    # Decode the response body
    if decoded:
        charset = match1(
            response.getheader('Content-Type'), r'charset=([\w-]+)'
        )
        if charset is not None:
            data = data.decode(charset)
        else:
            data = data.decode('utf-8')

    return data

def clear_dag_runs():
    """
    
    """
    session = settings.Session()
    drs = session.query(DagRun).filter(
        DagRun.dag_id.in_(DAG_IDS),
    ).all()
    for dr in drs:
        logging.info('Deleting DagRun :: {}'.format(dr))
        session.delete(dr)

def print_stats(self):
        """
        
        """
        session = settings.Session()
        TI = TaskInstance
        tis = (
            session
            .query(TI)
            .filter(TI.dag_id.in_(DAG_IDS))
            .all()
        )
        successful_tis = [x for x in tis if x.state == State.SUCCESS]
        ti_perf = [(ti.dag_id, ti.task_id, ti.execution_date,
                    (ti.queued_dttm - self.start_date).total_seconds(),
                    (ti.start_date - self.start_date).total_seconds(),
                    (ti.end_date - self.start_date).total_seconds(),
                    ti.duration) for ti in successful_tis]
        ti_perf_df = pd.DataFrame(ti_perf, columns=['dag_id', 'task_id',
                                                    'execution_date',
                                                    'queue_delay',
                                                    'start_delay', 'land_time',
                                                    'duration'])

        print('Performance Results')
        print('###################')
        for dag_id in DAG_IDS:
            print('DAG {}'.format(dag_id))
            print(ti_perf_df[ti_perf_df['dag_id'] == dag_id])
        print('###################')
        if len(tis) > len(successful_tis):
            print("WARNING!! The following task instances haven't completed")
            print(pd.DataFrame([(ti.dag_id, ti.task_id, ti.execution_date, ti.state)
                  for ti in filter(lambda x: x.state != State.SUCCESS, tis)],
                  columns=['dag_id', 'task_id', 'execution_date', 'state']))

        session.commit()

def resetdb():
    """
    
    """
    from airflow import models

    # alembic adds significant import time, so we import it lazily
    from alembic.migration import MigrationContext

    log.info("Dropping tables that exist")

    models.base.Base.metadata.drop_all(settings.engine)
    mc = MigrationContext.configure(settings.engine)
    if mc._version.exists(settings.engine):
        mc._version.drop(settings.engine)

    from flask_appbuilder.models.sqla import Base
    Base.metadata.drop_all(settings.engine)

    initdb()

def delete_transfer_job(self, job_name, project_id):
        """
        
        """

        return (
            self.get_conn()
            .transferJobs()
            .patch(
                jobName=job_name,
                body={
                    PROJECT_ID: project_id,
                    TRANSFER_JOB: {STATUS1: GcpTransferJobsStatus.DELETED},
                    TRANSFER_JOB_FIELD_MASK: STATUS1,
                },
            )
            .execute(num_retries=self.num_retries)
        )

def list_transfer_job(self, filter):
        """
        
        """
        conn = self.get_conn()
        filter = self._inject_project_id(filter, FILTER, FILTER_PROJECT_ID)
        request = conn.transferJobs().list(filter=json.dumps(filter))
        jobs = []

        while request is not None:
            response = request.execute(num_retries=self.num_retries)
            jobs.extend(response[TRANSFER_JOBS])

            request = conn.transferJobs().list_next(previous_request=request, previous_response=response)

        return jobs

def max_runs_reached(self):
        """
        
        """
        if self._max_runs == -1:  # Unlimited runs.
            return False
        for file_path in self._file_paths:
            if self._run_count[file_path] < self._max_runs:
                return False
        if self._run_count[self._heart_beat_key] < self._max_runs:
            return False
        return True

def clear_not_launched_queued_tasks(self, session=None):
        """
        
        """
        queued_tasks = session\
            .query(TaskInstance)\
            .filter(TaskInstance.state == State.QUEUED).all()
        self.log.info(
            'When executor started up, found %s queued task instances',
            len(queued_tasks)
        )

        for task in queued_tasks:
            dict_string = (
                "dag_id={},task_id={},execution_date={},airflow-worker={}".format(
                    AirflowKubernetesScheduler._make_safe_label_value(task.dag_id),
                    AirflowKubernetesScheduler._make_safe_label_value(task.task_id),
                    AirflowKubernetesScheduler._datetime_to_label_safe_datestring(
                        task.execution_date
                    ),
                    self.worker_uuid
                )
            )
            kwargs = dict(label_selector=dict_string)
            pod_list = self.kube_client.list_namespaced_pod(
                self.kube_config.kube_namespace, **kwargs)
            if len(pod_list.items) == 0:
                self.log.info(
                    'TaskInstance: %s found in queued state but was not launched, '
                    'rescheduling', task
                )
                session.query(TaskInstance).filter(
                    TaskInstance.dag_id == task.dag_id,
                    TaskInstance.task_id == task.task_id,
                    TaskInstance.execution_date == task.execution_date
                ).update({TaskInstance.state: State.NONE})
