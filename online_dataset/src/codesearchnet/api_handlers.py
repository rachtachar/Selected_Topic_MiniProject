"""
Module: api_handlers.py
Sourced from Hugging Face: mteb/CodeSearchNetRetrieval
"""
import os
import sys
import re
import json
import time

def closest_ds_partition(
        table, ds, before=True, schema="default",
        metastore_conn_id='metastore_default'):
    """
    
    """
    from airflow.hooks.hive_hooks import HiveMetastoreHook
    if '.' in table:
        schema, table = table.split('.')
    hh = HiveMetastoreHook(metastore_conn_id=metastore_conn_id)
    partitions = hh.get_partitions(schema=schema, table_name=table)
    if not partitions:
        return None
    part_vals = [list(p.values())[0] for p in partitions]
    if ds in part_vals:
        return ds
    else:
        parts = [datetime.datetime.strptime(pv, '%Y-%m-%d')
                 for pv in part_vals]
        target_dt = datetime.datetime.strptime(ds, '%Y-%m-%d')
        closest_ds = _closest_date(target_dt, parts, before_target=before)
        return closest_ds.isoformat()

def get_database_hook(self):
        """
        
        """
        if self.database_type == 'postgres':
            self.db_hook = PostgresHook(postgres_conn_id=self.db_conn_id,
                                        schema=self.database)
        else:
            self.db_hook = MySqlHook(mysql_conn_id=self.db_conn_id,
                                     schema=self.database)
        return self.db_hook

def get_head(repo_path):
    """"""
    try:
        ref = open(os.path.join(repo_path, '.git', 'HEAD'), 'r').read().strip()[5:].split('/')
        branch = ref[-1]
        commit = open(os.path.join(repo_path, '.git', *ref), 'r').read().strip()[:7]
        return branch, commit
    except:
        return None

def as_dict(
            self, display_source=False, display_sensitive=False, raw=False):
        """
        
        """
        cfg = {}
        configs = [
            ('default', self.airflow_defaults),
            ('airflow.cfg', self),
        ]

        for (source_name, config) in configs:
            for section in config.sections():
                sect = cfg.setdefault(section, OrderedDict())
                for (k, val) in config.items(section=section, raw=raw):
                    if display_source:
                        val = (val, source_name)
                    sect[k] = val

        # add env vars and overwrite because they have priority
        for ev in [ev for ev in os.environ if ev.startswith('AIRFLOW__')]:
            try:
                _, section, key = ev.split('__')
                opt = self._get_env_var_option(section, key)
            except ValueError:
                continue
            if not display_sensitive and ev != 'AIRFLOW__CORE__UNIT_TEST_MODE':
                opt = '< hidden >'
            elif raw:
                opt = opt.replace('%', '%%')
            if display_source:
                opt = (opt, 'env var')
            cfg.setdefault(section.lower(), OrderedDict()).update(
                {key.lower(): opt})

        # add bash commands
        for (section, key) in self.as_command_stdout:
            opt = self._get_cmd_option(section, key)
            if opt:
                if not display_sensitive:
                    opt = '< hidden >'
                if display_source:
                    opt = (opt, 'cmd')
                elif raw:
                    opt = opt.replace('%', '%%')
                cfg.setdefault(section, OrderedDict()).update({key: opt})
                del cfg[section][key + '_cmd']

        return cfg

def get_database(self, instance, database, project_id=None):
        """
        
        """
        return self.get_conn().databases().get(
            project=project_id,
            instance=instance,
            database=database
        ).execute(num_retries=self.num_retries)

def dailymotion_download(url, output_dir='.', merge=True, info_only=False, **kwargs):
    """
    """

    html = get_content(rebuilt_url(url))
    info = json.loads(match1(html, r'qualities":({.+?}),"'))
    title = match1(html, r'"video_title"\s*:\s*"([^"]+)"') or \
            match1(html, r'"title"\s*:\s*"([^"]+)"')
    title = unicodize(title)

    for quality in ['1080','720','480','380','240','144','auto']:
        try:
            real_url = info[quality][1]["url"]
            if real_url:
                break
        except KeyError:
            pass

    mime, ext, size = url_info(real_url)

    print_info(site_info, title, mime, size)
    if not info_only:
        download_urls([real_url], title, ext, size, output_dir=output_dir, merge=merge)

def run(self, hql, parameters=None):
        """
        
        """
        return super().run(self._strip_sql(hql), parameters)
