# Copyright L.P.Klyne 2013 
# Licenced under 3 clause BSD licence 

# $Id: Utils.py 2610 2008-08-11 20:04:17Z graham.klyne $

import pkg_resources
import logging
import string
from os.path import exists

_log = logging.getLogger( "WebBrickGateway.Utils" )

# We log known templates we have attempted to use in here so that
# we can use defaults if none existant.
_knownTemplates = dict()

def validateTemplateDirectory( templatePath ):
    # Make sure has __init__.py
    if not exists("%s/templates/__init__.pyc" % templatePath)and not exists("%s/templates/__init__.py" % templatePath):
        # create
        f = open( "%s/templates/__init__.py" % templatePath, "w" )
        f.write("#AutoCreated")
        f.close()

def checkTemplateName( fullTemplateName ):
    result = None
    # attempt to load template
    # if success then set up known templates.
    # else store None
    if fullTemplateName:
        try:
            # locate final period and split string.
            ps = string.rsplit( fullTemplateName, ".", 1 )
            if len(ps) > 1:
                _log.debug( 'look for template %s ' %(fullTemplateName) )

                if pkg_resources.resource_exists(ps[0], ps[1]+'.kid'):
                    _log.debug( 'template %s exists' %(fullTemplateName) )
                    result = fullTemplateName    # success 

        except ImportError, ex:
            # does not exists use default.
            _log.debug( 'Import error loading %s' %(fullTemplateName) )
            pass

        except Exception, ex:
            _log.exception( 'error loading %s' %(fullTemplateName) )

    return result

# This not currently called?
def tryLoadTemplate( fullTemplateName ):
    if not _knownTemplates.has_key( fullTemplateName ):
        # attempt to load template
        # if success then set up known templates.
        # else store None
        try:
            # locate final period and split string.
            ps = string.rsplit( fullTemplateName, ".", 1 )
            _log.debug( 'look for template %s in %s' %(ps[1], ps[0]) )

            if pkg_resources.resource_exists(ps[0], ps[1]+'.kid'):
                _log.debug( 'template %s exists' %(fullTemplateName) )
                _knownTemplates[fullTemplateName] = fullTemplateName    # success 

        except ImportError, ex:
            # does not exists use default.
            _log.exception( 'error loading %s' %(fullTemplateName) )
            pass

        except Exception, ex:
            _log.exception( 'error loading %s' %(fullTemplateName) )

        if not _knownTemplates.has_key( fullTemplateName ):
            _log.debug( 'template %s MISSING' %(fullTemplateName) )
            _knownTemplates[fullTemplateName] = None    # error

    return _knownTemplates[fullTemplateName]    # allows mapping names

def locateTemplateName( module, templateName ):
    # try relative
    tmpl = "%s.%s" % (module,templateName)
    _log.debug( 'look in %s for template %s' %(module, templateName) )
    if checkTemplateName( tmpl ):
        return tmpl
    elif checkTemplateName( templateName ):
        # then absolute
        return templateName
    else:
        # try loosing leading part and recurse
        idx = templateName.find('.' )
        if idx >= 0:
            return locateTemplateName( module, templateName[idx+1:] )
    return None

def getTemplateName( module, templateName ):
    result = None

    # first assume templateName is relative to module
    # second try absolute
    # then strip a leading component and recurse

    # TODO timeout entries in the known templates so we see new ones in different locations

    tmpl = "%s.%s" % (module,templateName)
    if _knownTemplates.has_key( tmpl ):
        # it is this one.
        # we may of ended up mapping the name
        result = _knownTemplates[tmpl]
    else:
        result = locateTemplateName( module, templateName )
        if result:
            _knownTemplates[tmpl] = result

    return result

# $Id: Utils.py 2610 2008-08-11 20:04:17Z graham.klyne $
