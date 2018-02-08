'''
Created on jan 22, 2018

@author: NNA
'''

import cast.application
import logging
import ast
import re

class ExtensionApplication(cast.application.ApplicationLevelExtension):

    def end_application(self, application):
        logging.info("Running code at the end of an Application")
        self.CreatejmsQueuelink(application,'Java_JMS_QueueCall')
        self.Createjmslink(application,'Java_JMS_QueueconnectionFactory')
        
    def Createjmslink(self,application,jmstext):
        jmsObjectReferences = list(application.search_objects(category=jmstext, load_properties= True))
        javaMethodObjectReferences = list(application.search_objects(category='JV_METHOD', load_properties=False))
        if len(jmsObjectReferences)>0:
            for jmsObject in jmsObjectReferences :
                    logging.info('inside method_name --> ' + jmsObject.get_name())
                    prop_type = jmsObject.get_property('JmsQueueProperties.sourcefile')
                    if prop_type.lower() == 'properties':
                        method_name = jmsObject.name()
                        for javaObject in javaMethodObjectReferences : 
                            javamethod_name = javaObject.get_name()
                            if javamethod_name ==  method_name:
                                logging.info('inside 2 method_name --> '+javamethod_name)
                                cast.application.create_link("callLink", jmsObject, javaObject, bookmark=None) 
                                logging.debug("link created-->" + method_name)
                                
    def CreatejmsQueuelink(self,application,jmstext):
        jmsObjectReferences = list(application.search_objects(category=jmstext, load_properties= True))
        javaMethodObjectReferences = list(application.search_objects(category='JSP_PROPERTY_MAPPING', load_properties=False))
        if len(jmsObjectReferences)>0:
            for jmsObject in jmsObjectReferences :
                    prop_type = jmsObject.get_property('JmsQueueProperties.sourcefile')
                    if prop_type.lower() == 'properties':
                        method_name = jmsObject.get_name()
                        for javaObject in javaMethodObjectReferences : 
                            javamethod_name = javaObject.get_name()
                            if javamethod_name ==  method_name:
                                cast.application.create_link("callLink", jmsObject, javaObject, bookmark=None) 
                                logging.debug("link created-->" + method_name)
                       
                       