"""
Module: string_utils.py
Sourced from Hugging Face: mteb/CodeSearchNetRetrieval
"""
import os
import sys
import re
import json
import time

def matchall(text, patterns):
    """
    """

    ret = []
    for pattern in patterns:
        match = re.findall(pattern, text)
        ret += match

    return ret

def execute(self, context):
        """
        
        """
        hook = GoogleCloudStorageHook(
            google_cloud_storage_conn_id=self.google_cloud_storage_conn_id,
            delegate_to=self.delegate_to)

        hook.upload(
            bucket_name=self.bucket,
            object_name=self.dst,
            mime_type=self.mime_type,
            filename=self.src,
            gzip=self.gzip,
        )

def _get_field(self, field_name, default=None):
        """
        
        """
        full_field_name = 'extra__grpc__{}'.format(field_name)
        if full_field_name in self.extras:
            return self.extras[full_field_name]
        else:
            return default

def stop_proxy(self):
        """
        
        """
        if not self.sql_proxy_process:
            raise AirflowException("The sql proxy is not started yet")
        else:
            self.log.info("Stopping the cloud_sql_proxy pid: %s",
                          self.sql_proxy_process.pid)
            self.sql_proxy_process.kill()
            self.sql_proxy_process = None
        # Cleanup!
        self.log.info("Removing the socket directory: %s",
                      self.cloud_sql_proxy_socket_directory)
        shutil.rmtree(self.cloud_sql_proxy_socket_directory, ignore_errors=True)
        if self.sql_proxy_was_downloaded:
            self.log.info("Removing downloaded proxy: %s", self.sql_proxy_path)
            # Silently ignore if the file has already been removed (concurrency)
            try:
                os.remove(self.sql_proxy_path)
            except OSError as e:
                if not e.errno == errno.ENOENT:
                    raise
        else:
            self.log.info("Skipped removing proxy - it was not downloaded: %s",
                          self.sql_proxy_path)
        if os.path.isfile(self.credentials_path):
            self.log.info("Removing generated credentials file %s",
                          self.credentials_path)
            # Here file cannot be delete by concurrent task (each task has its own copy)
            os.remove(self.credentials_path)

def get_conn(self):
        """
        
        """
        conn = self.get_connection(self.mysql_conn_id)
        conn_config = {
            "user": conn.login,
            "passwd": conn.password or '',
            "host": conn.host or 'localhost',
            "db": self.schema or conn.schema or ''
        }

        if not conn.port:
            conn_config["port"] = 3306
        else:
            conn_config["port"] = int(conn.port)

        if conn.extra_dejson.get('charset', False):
            conn_config["charset"] = conn.extra_dejson["charset"]
            if (conn_config["charset"]).lower() == 'utf8' or\
                    (conn_config["charset"]).lower() == 'utf-8':
                conn_config["use_unicode"] = True
        if conn.extra_dejson.get('cursor', False):
            if (conn.extra_dejson["cursor"]).lower() == 'sscursor':
                conn_config["cursorclass"] = MySQLdb.cursors.SSCursor
            elif (conn.extra_dejson["cursor"]).lower() == 'dictcursor':
                conn_config["cursorclass"] = MySQLdb.cursors.DictCursor
            elif (conn.extra_dejson["cursor"]).lower() == 'ssdictcursor':
                conn_config["cursorclass"] = MySQLdb.cursors.SSDictCursor
        local_infile = conn.extra_dejson.get('local_infile', False)
        if conn.extra_dejson.get('ssl', False):
            # SSL parameter for MySQL has to be a dictionary and in case
            # of extra/dejson we can get string if extra is passed via
            # URL parameters
            dejson_ssl = conn.extra_dejson['ssl']
            if isinstance(dejson_ssl, six.string_types):
                dejson_ssl = json.loads(dejson_ssl)
            conn_config['ssl'] = dejson_ssl
        if conn.extra_dejson.get('unix_socket'):
            conn_config['unix_socket'] = conn.extra_dejson['unix_socket']
        if local_infile:
            conn_config["local_infile"] = 1
        conn = MySQLdb.connect(**conn_config)
        return conn

def get_conn(self):
        """
        
        """
        conn = self.get_connection(self.vertica_conn_id)
        conn_config = {
            "user": conn.login,
            "password": conn.password or '',
            "database": conn.schema,
            "host": conn.host or 'localhost'
        }

        if not conn.port:
            conn_config["port"] = 5433
        else:
            conn_config["port"] = int(conn.port)

        conn = connect(**conn_config)
        return conn

def parameterized_config(template):
    """
    
    """
    all_vars = {k: v for d in [globals(), locals()] for k, v in d.items()}
    return template.format(**all_vars)

def utcnow():
    """
    
    """

    # pendulum utcnow() is not used as that sets a TimezoneInfo object
    # instead of a Timezone. This is not pickable and also creates issues
    # when using replace()
    d = dt.datetime.utcnow()
    d = d.replace(tzinfo=utc)

    return d
