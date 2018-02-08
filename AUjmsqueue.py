'''
Created on DEC 29, 2017

@author: NNA
'''

import cast.analysers.jee
import cast.application
import cast.analysers.log as LOG
import os
from cast.analysers import Member,Bookmark
from setuptools.sandbox import _file
import xml.etree.ElementTree as ET
from Cython.Compiler.Options import annotate


def get_overriden(_type, member):
    """
    Get the ancestor's member this member overrides
    """
    member_name = member.get_name()
    
    result = []
    
    for parent in _type.get_inherited_types():
        
        for child in parent.get_children():
            if child.get_name() == member_name:
                result.append(child)
        
        result += get_overriden(parent, member)
        
    return result

class search(cast.analysers.jee.Extension):
    def __init__(self):
        self.result = None
        self.count = 0
        self.jmstext=""
        self.jmsmetamodeltext =""
        
               
    def start_analysis(self,options):
        LOG.info('Successfully jms analyzer Started')
        options.add_classpath('jars')
        
    
    def start_properties_file(self, file):
        LOG.debug('Successfully Prop file')
        if file.get_name().endswith('.properties'):
            if (os.path.isfile(file.get_path())):
                props = self.loadprop(file)
                LOG.debug(str(props))
                self.Createpropjms(file, props, 'jms.queue.name', 'Java_JMS_QueueCall')
                self.Createpropjms(file, props, 'jms.queue.connection.factory', 'Java_JMS_QueueconnectionFactory')
               
              
                    
   
    def Createpropjms(self,file, prop, key, mtype):
        try :
            if key in prop:
                self.count= self.count+1
                jmsObj = cast.analysers.CustomObject()
                jmsObj.set_name(prop[key])
                jmsObj.set_type(mtype)
                jmsObj.set_parent(file)
                parentFile = file.get_position().get_file() 
                self.fielPath = parentFile.get_fullname()
                jmsObj.set_guid(self.fielPath+prop[key]+str(self.count))
                jmsObj.save()
                jmsObj.save_position(file.get_position())
                Parsing.addtype_property(jmsObj, 'sourcetype', file.get_name().split('\\')[-1] )
                Parsing.addtype_property(jmsObj, 'sourcefile', 'Properties')
                LOG.info('Creating  JMS  '+ prop[key] )  
               
        except:
            return 
         
       
    # receive a java parser from platform
    @cast.Event('com.castsoftware.internal.platform', 'jee.java_parser')
    def receive_java_parser(self, parser):
        self.java_parser = parser
        LOG.info('Successfully receive_java_parser')
        pass
        

    def loadprop(self, file):
        sep = "="
        comment_char= "#"
        props = {}
        with open(file.get_name(), "rt") as f:
            for line in f:
                l = line.strip()
                if l and not l.startswith(comment_char):
                    key_value = l.split(sep)
                    key = key_value[0].strip()
                    value = sep.join(key_value[1:]).strip().strip('"') 
                    props[key] = value 
        return props                          
    
    def end_analysis(self):
        self.result
        LOG.info("JMS Analyzer  Ended")
        
        
class Parsing():  
    
    @staticmethod
    def add_property(obj,  prop, ele ):
        if ele.get(prop) is not None:
            LOG.debug(' - %s: %s' % (prop, ele.get(prop)))
            obj.save_property('JmsQueueProperties.%s' % prop, ele.get(prop))
        else:
            obj.save_property('JmsQueueProperties.%s' % prop, "None")
            
    @staticmethod
    def add_jmsproperty(obj, ele, prop, proptext ):
        if ele.get(proptext) is not None:
            LOG.debug(' - %s: %s' % (prop, ele.get(proptext)))
            obj.save_property('JmsQueueProperties.%s' % prop, ele.get(proptext) )
        else:
            obj.save_property('JmsQueueProperties.%s' % prop, "None")  
            
            
    @staticmethod
    def addtype_property(obj,  prop, proptext):
        if proptext is not None:
            obj.save_property('JmsQueueProperties.%s' % prop, proptext)
        else:
            obj.save_property('JmsQueueProperties.%s' % prop, "None") 
            
