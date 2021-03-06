# -*- coding: utf-8 -*-

# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php

# Copyright 2008, Frank Scholz <coherence@beebits.net>

from twisted.internet import task
from twisted.internet import reactor
from twisted.web import resource, static

from coherence import __version__

from coherence.extern.et import ET, indent

from coherence.upnp.services.servers.switch_power_server import SwitchPowerServer

from coherence.upnp.devices.basics import RootDeviceXML, DeviceHttpRoot, BasicDeviceMixin

import coherence.extern.louie as louie

from coherence import log

class HttpRoot(DeviceHttpRoot):
    logCategory = 'binarylight'


class BinaryLight(log.Loggable,BasicDeviceMixin):
    logCategory = 'binarylight'

    def __init__(self, coherence, backend, **kwargs):
        self.coherence = coherence
        self.device_type = 'BinaryLight'
        self.version = 1
        #log.Loggable.__init__(self)

        try:
            self.uuid = kwargs['uuid']
        except KeyError:
            from coherence.upnp.core.uuid import UUID
            self.uuid = UUID()

        self.backend = None

        self.icons = kwargs.get('iconlist', kwargs.get('icons', []))
        if len(self.icons) == 0:
            if kwargs.has_key('icon'):
                self.icons.append(kwargs['icon'])

        louie.connect( self.init_complete, 'Coherence.UPnP.Backend.init_completed', louie.Any)
        reactor.callLater(0.2, self.fire, backend, **kwargs)

    def fire(self,backend,**kwargs):
        if kwargs.get('no_thread_needed',False) == False:
            """ this could take some time, put it in a  thread to be sure it doesn't block
                as we can't tell for sure that every backend is implemented properly """

            from twisted.internet import threads
            d = threads.deferToThread(backend, self, **kwargs)

            def backend_ready(backend):
                self.backend = backend

            def backend_failure(x):
                self.warning('backend not installed, %s activation aborted' % self.device_type)
                self.debug(x)

            d.addCallback(backend_ready)
            d.addErrback(backend_failure)

            # FIXME: we need a timeout here so if the signal we wait for not arrives we'll
            #        can close down this device
        else:
            self.backend = backend(self, **kwargs)

    def init_complete(self, backend):
        if self.backend != backend:
            return
        self._services = []
        self._devices = []

        try:
            self.switch_power_server = SwitchPowerServer(self)
            self._services.append(self.switch_power_server)
        except LookupError,msg:
            self.warning( 'SwitchPowerServer', msg)
            raise LookupError,msg

        upnp_init = getattr(self.backend, "upnp_init", None)
        if upnp_init:
            upnp_init()


        self.web_resource = HttpRoot(self)
        self.coherence.add_web_resource( str(self.uuid)[5:], self.web_resource)


        version = self.version
        while version > 0:
            self.web_resource.putChild( 'description-%d.xml' % version,
                                    RootDeviceXML( self.coherence.hostname,
                                    str(self.uuid),
                                    self.coherence.urlbase,
                                    self.device_type, version,
                                    friendly_name=self.backend.name,
                                    model_description='Coherence UPnP %s' % self.device_type,
                                    model_name='Coherence UPnP %s' % self.device_type,
                                    services=self._services,
                                    devices=self._devices,
                                    icons=self.icons))
            version -= 1


        self.web_resource.putChild('SwitchPower', self.switch_power_server)

        for icon in self.icons:
            if icon.has_key('url'):
                if icon['url'].startswith('file://'):
                    self.web_resource.putChild(os.path.basename(icon['url']),
                                               static.File(icon['url'][7:]))

        self.register()
        self.warning("%s %s (%s) activated" % (self.backend.name, self.device_type, self.backend))
