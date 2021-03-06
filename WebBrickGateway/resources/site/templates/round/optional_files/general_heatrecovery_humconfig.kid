<?python 
kid.enable_import()
import WebBrickGateway.templates.widgets_round
import zone_lists
import zoneControl_embed

layout_params['left_title'] = "Zones"
layout_params['show_left'] = True
layout_params['show_top'] = True
layout_params['show_bottom'] = True
layout_params['itouch_icon'] = "funciconventilation.png"

?>

<!-- !  This requires HRV to be setup in event despatch, with the following files:
            heatrecovery_ventilation_inputs.xml
            heatrecovery_ventilation_outputs.xml 
            -->

<html py:layout="'sitelayout3.kid'" xmlns:py="http://purl.org/kid/ns#"  xmlns:wb="http://id.webbrick.co.uk/" 
        py:extends="zone_lists, zoneControl_embed, WebBrickGateway.templates.widgets_round">
    <div py:match="item.tag == '{http://id.webbrick.co.uk/}leftboxcontent'" id="leftboxcontent">
        <!-- !Insert content for left box in here -->
        ${output_zone_links("", "ventilation")}
    </div>

    <div py:match="item.tag == '{http://id.webbrick.co.uk/}topboxcontent'" id="topboxcontent">
        <!-- !Insert content for top right box in here -->
        
        <table>
            <tr>
                <td style="margin-left:5px; text-align:left">
                    <h1>Heat Recovery Humidity Sensor Configuration</h1>
                </td>
            </tr>
        </table>    
        <table id="scheduleboxtable">
            <tr>
                <th>&nbsp;</th>
                <th>Sensor</th>
                <th>Threshold</th>
                <th>Current</th>
                <th>&nbsp;</th>
            </tr>
            <tr>
                <td class="buttoncapleft"/>
                <td class="buttonbody">
                    Humidity 1
                </td>
                <td class="buttonbody">
                    <wb:numericEntry 
                            prefix="" format="##.#" postfix="%"
                            noPolling="yes"
                            wbSource='/eventstate/general/ventilation/hum/1/threshold'
                            wbTarget='/sendevent/general/ventilation/hum/1/threshold?type=http://id.webbrick.co.uk/events/config/set'
                                />
                </td>
                <td class="buttonbody">
                    <wb:numericDisplay
 
                            prefix="" format="##.#" postfix="%"
                            noPolling="yes"
                            wbSource='/eventstate/general/ventilation/hum/1/level'
                                />
                </td>
                <td class="buttoncapright"/>
            </tr>
            <tr>
                <td class="buttoncapleft"/>
                <td class="buttonbody">
                    Humidity 2
                </td>
                <td class="buttonbody">
                    <wb:numericEntry 
                            prefix="" format="##.#" postfix="%"
                            noPolling="yes"
                            wbSource='/eventstate/general/ventilation/hum/2/threshold'
                            wbTarget='/sendevent/general/ventilation/hum/2/threshold?type=http://id.webbrick.co.uk/events/config/set'
                                />
                </td>
                <td class="buttonbody">
                    <wb:numericDisplay
 
                            prefix="" format="##.#" postfix="%"
                            noPolling="yes"
                            wbSource='/eventstate/general/ventilation/hum/2/level'
                                />
                </td>
                <td class="buttoncapright"/>
            </tr>
            <tr>
                <td class="buttoncapleft"/>
                <td class="buttonbody">
                    Humidity 3
                </td>
                <td class="buttonbody">
                    <wb:numericEntry 
                            prefix="" format="##.#" postfix="%"
                            noPolling="yes"
                            wbSource='/eventstate/general/ventilation/hum/3/threshold'
                            wbTarget='/sendevent/general/ventilation/hum/3/threshold?type=http://id.webbrick.co.uk/events/config/set'
                                />
                </td>
                <td class="buttonbody">
                    <wb:numericDisplay
 
                            prefix="" format="##.#" postfix="%"
                            noPolling="yes"
                            wbSource='/eventstate/general/ventilation/hum/3/level'
                                />
                </td>
                <td class="buttoncapright"/>
            </tr>
            <tr>
                <td class="buttoncapleft"/>
                <td class="buttonbody">
                    Humidity 4
                </td>
                <td class="buttonbody">
                    <wb:numericEntry 
                            prefix="" format="##.#" postfix="%"
                            noPolling="yes"
                            wbSource='/eventstate/general/ventilation/hum/4/threshold'
                            wbTarget='/sendevent/general/ventilation/hum/4/threshold?type=http://id.webbrick.co.uk/events/config/set'
                                />
                </td>
                <td class="buttonbody">
                    <wb:numericDisplay
 
                            prefix="" format="##.#" postfix="%"
                            noPolling="yes"
                            wbSource='/eventstate/general/ventilation/hum/4/level'
                                />
                </td>
                <td class="buttoncapright"/>
            </tr>
        </table>
        <br>&nbsp;</br>
        <br>&nbsp;</br>
        <table>
            <colgroup span="3" width="34%"/>
            <tr>
                <td>
                    &nbsp;
                </td>
                <td>
                    &nbsp;
                </td>
                <td>
                    <wb:simpleLinkButton 
                            target="/template/heatrecovery_overview"  
                            >
                        Done
                    </wb:simpleLinkButton>
                </td>
            </tr>
        </table>
    </div>

    <div py:match="item.tag=='{http://id.webbrick.co.uk/}botboxcontent'" id="botboxcontent">
        <!-- !Insert content for bottom right box in here -->
        ${output_functional_links( "", "ventilation", [True,True,True,True,True] )}
    </div>

</html>
