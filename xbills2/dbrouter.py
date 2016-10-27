# -*- coding: utf-8 -*-

class MainDBRouter(object):
    def db_for_read(self, model, **hints):
        # if model._meta.app_label == 'core':
        #     return 'core'
        return 'default'

    def db_for_write(self, model, **hints):
        # if model._meta.app_label == 'core':
        #     return 'core'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_syncdb(self, db, model):
        if model._meta.app_label == 'core':
            return False
        if model._meta.app_label == 'dv':
            return False
        if model._meta.app_label == 'ipdhcp':
            return False
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name == 'core':
            return False
        if model_name == 'dv':
            return False
        if model_name == 'ipdhcp':
            return False
        return True

