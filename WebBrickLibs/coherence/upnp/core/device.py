# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php

# Copyright (C) 2006 Fluendo, S.A. (www.fluendo.com).
# Copyright 2006, Frank Scholz <coherence@beebits.net>

import urllib2
from urlparse import urlparse,urljoin
import time

from twisted.internet import defer

from coherence.upnp.core.service import Service
from coherence.upnp.core import utils
from coherence import log

import coherence.extern.louie as louie

ns = "urn:schemas-upnp-org:device-1-0"

class Device(log.Loggable):
    logCategory = 'device'

    def __init__(self, parent=None):
        self.parent = parent
        self.services = []
        #self.uid = self.usn[:-len(self.st)-2]
        self.friendly_name = ""
        self.device_type = ""
        self.udn = None
        self.detection_completed = False
        self.client = None
        self.icons = []
        self.devices = []

        louie.connect( self.receiver, 'Coherence.UPnP.Service.detection_completed', self)
        louie.connect( self.service_detection_failed, 'Coherence.UPnP.Service.detection_failed', self)

    def __repr__(self):
        return "embedded device %r %r, parent %r" % (self.friendly_name,self.device_type,self.parent)

    #def __del__(self):
    #    #print "Device removal completed"
    #    pass

    def remove(self,*args):
        self.info("removal of %s (%s)", self.friendly_name, self.udn)
        while len(self.devices)>0:
            device = self.devices.pop()
            self.debug("try to remove %r", device)
            device.remove()
        while len(self.services)>0:
            service = self.services.pop()
            self.debug("try to remove %r", service)
            service.remove()
        if self.client != None:
            louie.send('Coherence.UPnP.Device.remove_client', None, self.udn, self.client)
            self.client = None
        #del self

    def receiver( self, signal, *args, **kwargs):
        self.debug("device receiver called with %r %r", signal, kwargs)
        if self.detection_completed == True:
            return
        for s in self.services:
            if s.detection_completed == False:
                return
        self.detection_completed = True
        if self.parent != None:
            self.info("embedded device %r %r initialized, parent %r" % (self.friendly_name,self.device_type,self.parent))
        #louie.send('Coherence.UPnP.Device.detection_completed', None, device=self)
        if self.parent != None:
            louie.send('Coherence.UPnP.Device.detection_completed', self.parent, device=self)
        else:
            louie.send('Coherence.UPnP.Device.detection_completed', self, device=self)

    def service_detection_failed( self, device):
        self.remove()

    def get_id(self):
        return self.udn

    def get_root_id(self):
        if self.parent:
            return self.parent.get_id()
        return self.get_id()

    def get_root_device(self):
        if self.parent:
            return self.parent.get_root_device()
        return self

    def get_uuid(self):
        return self.udn[5:]

    def get_root_uuid(self):
        if self.parent:
            return self.parent.get_root_uuid()
        return self.get_uuid()

    def get_services(self):
        return self.services

    def add_service(self, service):
        self.debug("add_service %r", service)
        self.services.append(service)

    def remove_service_with_usn(self, service_usn):
        for service in self.services:
            if service.get_usn() == service_usn:
                self.services.remove(service)
                service.remove()
                break

    def add_device(self, device):
        self.debug("Device add_device %r", device)
        self.devices.append(device)

    def get_friendly_name(self):
        return self.friendly_name

    def get_device_type(self):
        return self.device_type

    def set_client(self, client):
        self.client = client

    def get_client(self):
        return self.client

    def renew_service_subscriptions(self):
        """ iterate over device's services and renew subscriptions """
        self.info("renew service subscriptions for %s" % self.friendly_name)
        now = time.time()
        for service in self.services:
            self.info("check service %r %r " % (service.id, service.get_sid()), service.get_timeout(), now)
            if service.get_sid() is not None:
                if service.get_timeout() < now:
                    self.debug("wow, we lost an event subscription for %s %s, " % (self.friendly_name, service.get_id()),
                          "maybe we need to rethink the loop time and timeout calculation?")
                if service.get_timeout() < now + 30 :
                    service.renew_subscription()

        for device in self.devices:
            device.renew_service_subscriptions()

    def unsubscribe_service_subscriptions(self):
        """ iterate over device's services and unsubscribe subscriptions """
        l = []
        for service in self.get_services():
            if service.get_sid() is not None:
                l.append(service.unsubscribe())
        dl = defer.DeferredList(l)
        return dl

    def parse_device(self, d):
        self.device_type = unicode(d.findtext('./{%s}deviceType' % ns))
        self.model_name = unicode(d.findtext('./{%s}modelName' % ns))
        self.friendly_name = unicode(d.findtext('./{%s}friendlyName' % ns))
        self.udn = d.findtext('.//{%s}UDN' % ns)

        icon_list = d.find('./{%s}iconList' % ns)
        if icon_list is not None:
            import urllib2
#            url_base = "%s://%s" % urllib2.urlparse.urlparse(self.get_location())[:2]
            for icon in icon_list.findall('./{%s}icon' % ns):
                try:
                    i = {}
                    i['mimetype'] = icon.find('./{%s}mimetype' % ns).text
                    i['width'] = icon.find('./{%s}width' % ns).text
                    i['height'] = icon.find('./{%s}height' % ns).text
                    i['depth'] = icon.find('./{%s}depth' % ns).text
                    i['url'] = icon.find('./{%s}url' % ns).text
                    i['url'] = urljoin(self.get_url_base(), i['url'])
#                    if i['url'].startswith('/'):
#                        i['url'] = ''.join((url_base,i['url']))
                    self.icons.append(i)
                    self.debug("adding icon %r for %r" % (i,self.friendly_name))
                except:
                    import traceback
                    self.debug(traceback.format_exc())
                    self.warning("device %r seems to have an invalid icon description, ignoring that icon" % self.friendly_name)

        serviceList = d.find('./{%s}serviceList' % ns)
        if serviceList:
            for service in serviceList.findall('./{%s}service' % ns):
                serviceType = service.findtext('{%s}serviceType' % ns)
                serviceId = service.findtext('{%s}serviceId' % ns)
                controlUrl = service.findtext('{%s}controlURL' % ns)
                eventSubUrl = service.findtext('{%s}eventSubURL' % ns)
                presentationUrl = service.findtext('{%s}presentationURL' % ns)
                scpdUrl = service.findtext('{%s}SCPDURL' % ns)
                """ check if values are somehow reasonable
                """
                if len(scpdUrl) == 0:
                    self.warning("service has no uri for its description")
                    continue
                if len(eventSubUrl) == 0:
                    self.warning("service has no uri for eventing")
                    continue
                if len(controlUrl) == 0:
                    self.warning("service has no uri for controling")
                    continue
                self.add_service(Service(serviceType, serviceId, self.get_url_base(),
                                         controlUrl,
                                         eventSubUrl, presentationUrl, scpdUrl, self))


            # now look for all sub devices
            embedded_devices = d.find('./{%s}deviceList' % ns)
            if embedded_devices:
                for d in embedded_devices.findall('./{%s}device' % ns):
                    embedded_device = Device(self)
                    self.add_device(embedded_device)
                    embedded_device.parse_device(d)

    def get_location(self):
        return self.parent.get_location()

    def get_url_base(self):
        return self.parent.get_url_base()

    def get_usn(self):
        return self.parent.get_usn()


class RootDevice(Device):

    def __init__(self, infos):
        self.usn = infos['USN']
        self.server = infos['SERVER']
        self.st = infos['ST']
        self.location = infos['LOCATION']
        self.manifestation = infos['MANIFESTATION']
        self.host = infos['HOST']
        self.root_detection_completed = False
        Device.__init__(self, None)
        louie.connect( self.device_detect, 'Coherence.UPnP.Device.detection_completed', self)
        # we need to handle root device completion
        # these events could be ourself or our children.
        self.parse_description()

    def __repr__(self):
        return "rootdevice %r %r %r, manifestation %r" % (self.friendly_name,self.st,self.host,self.manifestation)

    def get_usn(self):
        return self.usn

    def get_st(self):
        return self.st

    def get_location(self):
        return self.location

    def get_url_base(self):
        return self.url_base

    def get_host(self):
        return self.host

    def is_local(self):
        if self.manifestation == 'local':
            return True
        return False

    def is_remote(self):
        if self.manifestation != 'local':
            return True
        return False

    def device_detect( self, signal, *args, **kwargs):
        self.debug("device_detect %r", kwargs)
        if self.root_detection_completed == True:
            return
        self.debug("root_detection_completed %r", self.root_detection_completed)
        # our self is not complete yet
        if self.detection_completed == False:
            return
        self.debug("detection_completed %r", self.detection_completed)
        # now check child devices.
        self.debug("self.devices %r", self.devices)
        for d in self.devices:
            self.debug("check device %r %r", d.detection_completed, d)
            if d.detection_completed == False:
                return
        # now must be done, so notify root done
        self.root_detection_completed = True
        self.info("rootdevice %r %r %r initialized, manifestation %r" % (self.friendly_name,self.st,self.host,self.manifestation))
        louie.send('Coherence.UPnP.RootDevice.detection_completed', None, device=self)

    def add_device(self, device):
        self.debug("RootDevice add_device %r", device)
        self.devices.append(device)

    def get_devices(self):
        self.debug("RootDevice get_devices: %s", self.devices)
        return self.devices

    def parse_description(self):

        def gotPage(x):
            self.debug("got device description from %r" % self.location)
            data, headers = x
            tree = utils.parse_xml(data, 'utf-8').getroot()

            # This is the base for all relative URLs
            self.url_base = tree.findtext('./{%s}URLBase' % ns)
            if self.url_base is None or len(self.url_base) == 0:
                # not given in description so use location

                # TODO should we parse out only protocol and host or use as is
                # I think the url_base could contain part of a path as well.
                parsed = urlparse(self.location)
                # ensure has trailing slash
                self.url_base = "%s://%s/" % (parsed[0], parsed[1])
            self.debug("url_base %r" % self.url_base)

            d = tree.find('.//{%s}device' % ns)
            if d is not None:
                self.parse_device(d) # root device

        def gotError(failure, url):
            self.warning("error requesting %r", url)
            self.info(failure)

        utils.getPage(self.location).addCallbacks(gotPage, gotError, None, None, [self.location], None)
