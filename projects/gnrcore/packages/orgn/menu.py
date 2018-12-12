#!/usr/bin/python
# -*- coding: utf-8 -*-

def config(root,application=None):
    orgn = root.branch('!!Organizer',tags='admin')
    orgn.thpage('!!Annotations',table='orgn.annotation')
    orgn.thpage('!!Action types',table='orgn.action_type')
    orgn.thpage('!!Annotation types',table='orgn.annotation_type')
