<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python 
import sitetemplate
def getCurrentValue( uri ):
    """
    attempt to retrieve the current value of the uri passed
    """
    try:
        from WebBrickLibs.WbAccess import GetHTTPXmlDom
        from MiscLib.DomHelpers import getNamedNodeText
        dom = GetHTTPXmlDom( "localhost:8080", uri )    # need to know self address
        return getNamedNodeText(dom, 'val')
    except:
        from logging import getLogger
        getLogger( "WebBrickGateway.kid.useNoJavaScript" ).exception( "getCurrentValue" )
    return ''
?>

<html xmlns="http://www.w3.org/1999/xhtml" 
      xmlns:py="http://purl.org/kid/ns#" 
      xmlns:ui="ui" 
      xmlns:wb="http://id.webbrick.co.uk/"
      py:extends="sitetemplate" >

<head py:def="output_head(title)">
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>${title}</title>
    <?python 
        if not hasattr(self, 'javascript'):
            javascript = 'no'
    ?>
    <span py:if="javascript == 'no'">
        <link href="/static/css/panel_nojs.css" rel="stylesheet" type="text/css" />
    </span>

    <span py:if="javascript == 'yes'" py:strip="True">
        <link href="/static/css/panel.css" rel="stylesheet" type="text/css" />
        
        <script py:if="hasattr(self, 'debug')" src="/static/javascript/MochiKit.uncompressed.js" type="text/javascript"></script>

        <script py:if="not hasattr(self, 'debug')" src="/static/javascript/MochiKit.js" type="text/javascript"></script>

        <!-- WebBrick,js connects to onload and initialises panel elements -->
        <script src="/static/javascript/WebBrick.js" type="text/javascript"></script>
        <script src="/static/javascript/WbBackGround.js" type="text/javascript"></script>
        <script src="/static/javascript/WbButton.js" type="text/javascript"></script>
        <script src="/static/javascript/WbNumericDisplay.js" type="text/javascript"></script>
        <script src="/static/javascript/WbTimeDisplay.js" type="text/javascript"></script>
        <script src="/static/javascript/WbTextDisplay.js" type="text/javascript"></script>
        <script src="/static/javascript/WbNumericSlider.js" type="text/javascript"></script>
        <script src="/static/javascript/WbNumericBar.js" type="text/javascript"></script>
        <script src="/static/javascript/keyCheck.js" type="text/javascript"></script>
        <script src="/static/javascript/NumericPad.js" type="text/javascript"></script>
        <script src="/static/javascript/WbNumericEntry.js" type="text/javascript"></script>
        <script src="/static/javascript/WbTextEntry.js" type="text/javascript"></script>
        <script src="/static/javascript/WbTimeEntry.js" type="text/javascript"></script>
        <script src="/static/javascript/WbDayEntry.js" type="text/javascript"></script>
        <script src="/static/javascript/WbOnOffEntry.js" type="text/javascript"></script>
        <script src="/static/javascript/VlcPlugin.js" type="text/javascript"></script>
        <script src="/static/javascript/WbFlashMeter.js" type="text/javascript"></script>
        <script src="/static/javascript/WbFlashButton.js" type="text/javascript"></script>
        <script src="/static/javascript/WbStrings.js" type="text/javascript"></script>

        <script py:if="hasattr(self, 'debug')" src="/static/javascript/debug.js" type="text/javascript"></script>
    </span>
</head>

<table py:def="output_nav( location )" class="navTable">
    <tr>
        <wb:simpleLink width="20%" target="/">Home Menu</wb:simpleLink>
        <td class="infoBar" id="menuTitle">${location}</td>
        <!-- !Needs conversion for non javascript -->
        <td width="12%" class="navBarSmall" onClick="history.back()">Back</td>
        <wb:simpleLink width="12%" target="/template/templates/guide">Guide</wb:simpleLink>
    </tr>
    <tr class="rule"><td colspan='4' class="ruleBar">&nbsp;</td></tr>
</table>

<!-- The default site/location info bar -->
<table py:def="output_site_info_bar()" class="infoTable">
  <tr>
    <wb:textDisplay width='10%' wbSource="/local/time" prefix="" postfix="">Left</wb:textDisplay>
    <wb:textDisplay wbSource="/local/messages" prefix="" postfix="">Middle</wb:textDisplay>
	<td width='3%' wbType="Indicator" wbLoad="loadButton()"
		wbSource="/eventstate/occupants/home"
		stateVals="Away,Home"
		baseClassName="status"
		>
		&nbsp;
	</td>
	<td width='3%' wbType="Indicator" wbLoad="loadButton()"
		wbSource="/eventstate/heating/compensation"
		stateVals="WillRun,Suppress,Idle,Vacation"
		baseClassName="status"
		>
		&nbsp;
	</td>
    <wb:numericDisplay width='18%' wbSource="/eventstate/temperature/outside" prefix="Outside:" format="##.#" postfix="&ordm;C">Right</wb:numericDisplay>
  </tr>
</table>

<!-- for debugging what is not happening it can be usefull to see dictionaries at various points try self.__dict__ -->
<table py:def="output_dictionary( dct )">
    <tr py:for="ky in dct">
        <td>${ky}</td>
        <td py:if="isinstance( dct[ky], dict )" >${output_dictionary(dct[ky])}</td>
        <td py:if="not isinstance( dct[ky], dict )" >${str(dct[ky])}</td>
    </tr>
</table>

<span py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'" py:strip="" >
    <body py:if="javascript == 'yes'"
            py:attrs="item.items()" 
            wbType="WbBackGround" 
            wbSource="/eventstate/background">

        <div py:if="item.get('header')!='No'">
            <div py:if="tg_flash" class="flash" py:content="tg_flash"></div>
        </div>
        <div py:replace="[item.text] + item[:]"/>
    </body>

    <body py:if="javascript == 'no'"
            py:attrs="item.items()">
        <div py:if="item.get('header')!='No'">
            <div py:if="tg_flash" class="flash" py:content="tg_flash"></div>
        </div>
        <div py:replace="[item.text] + item[:]"/>
    </body>
</span>

<span py:match="item.tag=='{http://id.webbrick.co.uk/}simpleLink'" py:strip="" >
    <td py:if="flash == 'yes'"
                wbType="FlashLink" 
                wbSource="${item.get('wbSource')}"
                wbTarget="${item.get('target')}"
                width="200px"
                height="50px"
                title="${item.text}"
                flashMovie="/static/flash/SimpleISOButton2.swf"
                >
        &nbsp;
        ${item.getchildren()}
    </td>

    <td py:if="flash &lt;&gt; 'yes' and javascript == 'yes'"
                onClick="window.location=&apos;${item.get('target')}&apos;" 
                class="navBarSmall" 
                width="${item.get('width')}"
                >
        ${item.text}
        ${item.getchildren()}
    </td>
    <td py:if="javascript == 'no'"
                class="navBarSmall">
        <a href="${item.get('target')}">
            ${item.text}
            ${item.getchildren()}
        </a>
    </td>
</span>


<!-- entity conversion -->
<span py:match="item.tag=='{http://id.webbrick.co.uk/}textDisplay'" py:strip="" >
    <td py:if="javascript == 'yes'"
                wbType="Text" 
                wbLoad='loadTextDisplay(&apos;${item.get("prefix")}&apos;,&apos;${item.get("postfix")}&apos;)'
                wbSource="${item.get('wbSource')}"
                width="${item.get('width')}"
                >
        ${getCurrentValue( item.get('wbSource') )}
    </td>
    <td py:if="javascript == 'no'"
            py:content=" '%s%s%s' % ( item.get('prefix'), getCurrentValue( item.get('wbSource') ), item.get('postfix') )"
                wbLoadX='loadTextDisplay(&apos;${item.get("prefix")}&apos;,&apos;${item.get("postfix")}&apos;)'
                width="${item.get('width')}"
                class="textdisplay"
                >
        Text
    </td>
</span>

<span py:match="item.tag=='{http://id.webbrick.co.uk/}numericDisplay'" py:strip="" >
    <td py:if="javascript == 'yes'"
                wbType="Numeric" 
                wbLoad='loadNumericDisplay(&apos;${item.get("prefix")}&apos;,&apos;${item.get("format")}&apos;,&apos;${item.get("postfix")}&apos;)'
                wbSource="${item.get('wbSource')}"
                width="${item.get('width')}"
                py:content=" '%s%s%s' % ( item.get('prefix'), getCurrentValue( item.get('wbSource') ), item.get('postfix') )"
                >
        Number
    </td>
    <td py:if="javascript == 'no'"
            py:content=" '%s%s%s' % ( item.get('prefix'), getCurrentValue( item.get('wbSource') ), item.get('postfix') )"
                wbLoadX='loadNumericDisplay(&apos;${item.get("prefix")}&apos;,&apos;${item.get("format")}&apos;,&apos;${item.get("postfix")}&apos;)'
                width="${item.get('width')}"
                class="numericdisplay"
                >
        Number
    </td>
</span>

<span py:match="item.tag=='{http://id.webbrick.co.uk/}simpleButton'" py:strip="" >
    <td py:if="flash == 'yes'"
                wbType="FlashButton" 
                wbSource="${item.get('wbSource')}"
                wbTarget="${item.get('target')}"
                width="${item.get('width')}"
                height="50px"
                title="${item.text}"
                flashMovie="/static/flash/SimpleISOButton2.swf"
                >
        &nbsp;
        ${item.getchildren()}
    </td>

    <td py:if="flash &lt;&gt; 'yes' and javascript == 'yes'"
                wbType="PushButton" 
                wbSource="${item.get('wbSource')}"
                wbTarget="${item.get('wbTarget')}"
                width="${item.get('width')}"
                baseClassName="${item.get('baseClassName')}"
                py:content="item.text"
                >
        Button
    </td>

    <td py:if="javascript == 'no'"
            width="${item.get('width')}"
            class="button"
        >
        <a href="${item.get('wbTarget')}"
            py:content="item.text"
        >
            Button
        </a>
    </td>

</span>

</html>
