"""
Module: database_ops.py
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
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("""
            LOAD DATA LOCAL INFILE '{tmp_file}'
            INTO TABLE {table}
            """.format(tmp_file=tmp_file, table=table))
        conn.commit()

def cbs_download(url, output_dir='.', merge=True, info_only=False, **kwargs):
    """
    """

    html = get_content(url)
    pid = match1(html, r'video\.settings\.pid\s*=\s*\'([^\']+)\'')
    title = match1(html, r'video\.settings\.title\s*=\s*\"([^\"]+)\"')

    theplatform_download_by_pid(pid, title, output_dir=output_dir, merge=merge, info_only=info_only)

def _parse_s3_config(config_file_name, config_format='boto', profile=None):
    """
    
    """
    config = configparser.ConfigParser()
    if config.read(config_file_name):  # pragma: no cover
        sections = config.sections()
    else:
        raise AirflowException("Couldn't read {0}".format(config_file_name))
    # Setting option names depending on file format
    if config_format is None:
        config_format = 'boto'
    conf_format = config_format.lower()
    if conf_format == 'boto':  # pragma: no cover
        if profile is not None and 'profile ' + profile in sections:
            cred_section = 'profile ' + profile
        else:
            cred_section = 'Credentials'
    elif conf_format == 'aws' and profile is not None:
        cred_section = profile
    else:
        cred_section = 'default'
    # Option names
    if conf_format in ('boto', 'aws'):  # pragma: no cover
        key_id_option = 'aws_access_key_id'
        secret_key_option = 'aws_secret_access_key'
        # security_token_option = 'aws_security_token'
    else:
        key_id_option = 'access_key'
        secret_key_option = 'secret_key'
    # Actual Parsing
    if cred_section not in sections:
        raise AirflowException("This config file format is not recognized")
    else:
        try:
            access_key = config.get(cred_section, key_id_option)
            secret_key = config.get(cred_section, secret_key_option)
        except Exception:
            logging.warning("Option Error in parsing s3 config file")
            raise
        return access_key, secret_key

def is_bucket_updated(self, current_num_objects):
        """
        
        """

        if current_num_objects > self.previous_num_objects:
            # When new objects arrived, reset the inactivity_seconds
            # previous_num_objects for the next poke.
            self.log.info(
                '''
                New objects found at {} resetting last_activity_time.
                '''.format(os.path.join(self.bucket, self.prefix)))
            self.last_activity_time = get_time()
            self.inactivity_seconds = 0
            self.previous_num_objects = current_num_objects
        elif current_num_objects < self.previous_num_objects:
            # During the last poke interval objects were deleted.
            if self.allow_delete:
                self.previous_num_objects = current_num_objects
                self.last_activity_time = get_time()
                self.log.warning(
                    '''
                    Objects were deleted during the last
                    poke interval. Updating the file counter and
                    resetting last_activity_time.
                    '''
                )
            else:
                raise RuntimeError(
                    '''
                    Illegal behavior: objects were deleted in {} between pokes.
                    '''.format(os.path.join(self.bucket, self.prefix))
                )
        else:
            if self.last_activity_time:
                self.inactivity_seconds = (
                    get_time() - self.last_activity_time).total_seconds()
            else:
                # Handles the first poke where last inactivity time is None.
                self.last_activity_time = get_time()
                self.inactivity_seconds = 0

            if self.inactivity_seconds >= self.inactivity_period:
                if current_num_objects >= self.min_objects:
                    self.log.info(
                        '''
                        SUCCESS:
                        Sensor found {} objects at {}.
                        Waited at least {} seconds, with no new objects dropped.
                        '''.format(
                            current_num_objects,
                            os.path.join(self.bucket, self.prefix),
                            self.inactivity_period))
                    return True

                warn_msg = \
                    '''
                    FAILURE:
                    Inactivity Period passed,
                    not enough objects found in {}
                    '''.format(
                        os.path.join(self.bucket, self.prefix))
                self.log.warning(warn_msg)
                return False
            return False

def publish(self, project, topic, messages):
        """
        """
        body = {'messages': messages}
        full_topic = _format_topic(project, topic)
        request = self.get_conn().projects().topics().publish(
            topic=full_topic, body=body)
        try:
            request.execute(num_retries=self.num_retries)
        except HttpError as e:
            raise PubSubException(
                'Error publishing to topic {}'.format(full_topic), e)

def create_connection(self, session=None):
        """
        
        """
        connection = Connection(conn_id=self.db_conn_id)
        uri = self._generate_connection_uri()
        self.log.info("Creating connection %s", self.db_conn_id)
        connection.parse_from_uri(uri)
        session.add(connection)
        session.commit()

def execute(self, context):
        """
        
        """
        self.log.info('Tmp dir root location: \n %s', gettempdir())

        # Prepare env for child process.
        if self.env is None:
            self.env = os.environ.copy()

        airflow_context_vars = context_to_airflow_vars(context, in_env_var_format=True)
        self.log.info('Exporting the following env vars:\n%s',
                      '\n'.join(["{}={}".format(k, v)
                                 for k, v in
                                 airflow_context_vars.items()]))
        self.env.update(airflow_context_vars)

        self.lineage_data = self.bash_command

        with TemporaryDirectory(prefix='airflowtmp') as tmp_dir:
            with NamedTemporaryFile(dir=tmp_dir, prefix=self.task_id) as tmp_file:
                tmp_file.write(bytes(self.bash_command, 'utf_8'))
                tmp_file.flush()
                script_location = os.path.abspath(tmp_file.name)
                self.log.info('Temporary script location: %s', script_location)

                def pre_exec():
                    # Restore default signal disposition and invoke setsid
                    for sig in ('SIGPIPE', 'SIGXFZ', 'SIGXFSZ'):
                        if hasattr(signal, sig):
                            signal.signal(getattr(signal, sig), signal.SIG_DFL)
                    os.setsid()

                self.log.info('Running command: %s', self.bash_command)
                sub_process = Popen(
                    ['bash', tmp_file.name],
                    stdout=PIPE,
                    stderr=STDOUT,
                    cwd=tmp_dir,
                    env=self.env,
                    preexec_fn=pre_exec)

                self.sub_process = sub_process

                self.log.info('Output:')
                line = ''
                for raw_line in iter(sub_process.stdout.readline, b''):
                    line = raw_line.decode(self.output_encoding).rstrip()
                    self.log.info(line)

                sub_process.wait()

                self.log.info('Command exited with return code %s', sub_process.returncode)

                if sub_process.returncode:
                    raise AirflowException('Bash command failed')

        return line
