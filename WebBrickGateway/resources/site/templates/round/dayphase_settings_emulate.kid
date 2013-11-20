<?python 
kid.enable_import()
import WebBrickGateway.templates.widgets_round
import zone_lists
import zoneControl_embed

layout_params['left_title'] = "Categories"
layout_params['show_left'] = True
#layout_params['top_title'] = "Kitchen Heating Overview"
layout_params['show_top'] = True
#layout_params['bottom_title'] = "Kitchen Functions"
layout_params['show_bottom'] = True

?>

<html py:layout="'sitelayout3.kid'" xmlns:py="http://purl.org/kid/ns#"  xmlns:wb="http://id.webbrick.co.uk/" 
        py:extends="zone_lists, zoneControl_embed, WebBrickGateway.templates.widgets_round">
    <div py:match="item.tag == '{http://id.webbrick.co.uk/}leftboxcontent'" id="leftboxcontent">
        <!-- !Insert content for left box in here -->
        <ul class="divider29px">
            <li>
                <wb:simpleLinkList 
                        target="/template/sunrise_settings_overview" 
                        iconimage="zoneicons/zoneiconlivingroom.png"
                        >
                    Sunrise / Sunset
                </wb:simpleLinkList>
            </li>
            <li>
                <wb:simpleLinkList 
                        target="/template/dayphase_settings_overview" 
                        iconimage="zoneicons/zoneiconlivingroom.png"
                        >
                    Day Phase
                </wb:simpleLinkList>
            </li>
            <li>
                <wb:simpleLinkList 
                        target="/template/occupancy_settings_overview" 
                        iconimage="zoneicons/zoneiconlivingroom.png"
                        >
                    Occupancy
                </wb:simpleLinkList>
            </li>
            <li>
                <wb:simpleLinkList 
                        target="/template/installertools_settings_overview" 
                        iconimage="zoneicons/zoneiconlivingroom.png"
                        >
                    Installer Tools
                </wb:simpleLinkList>
            </li>
            <li>
                <wb:simpleLinkList 
                        target="/template/reboot_settings_overview" 
                        iconimage="zoneicons/zoneiconlivingroom.png"
                        >
                    Reboot
                </wb:simpleLinkList>
            </li>
        </ul>
    </div>

    <div py:match="item.tag == '{http://id.webbrick.co.uk/}topboxcontent'" id="topboxcontent">
        <!-- !Insert content for top right box in here -->
            
        <table>
            <colgroup span="3" width="33%"/>
            <tr>
                <td colspan="2" style="margin-left:5px; text-align:left"><h1>Day Phase Emulator</h1></td>
            </tr>
            <tr>
                <th>&nbsp;</th>
            </tr>
            <tr>
                <th colspan="3">
                    <wb:textDisplay 
                        colspan="2" 
                        wbSource="/eventstate/time/dayphaseext?attr=dayphasetext" 
                        prefix="Current Day Phase: " postfix=""
                        >Left
                    </wb:textDisplay>
                </th>
            </tr>
            <tr>
                <th>&nbsp;</th>
            </tr>
            <tr>
                <td>
                    <wb:simpleButton
                            wbTarget="/sendevent/time/isDark?type=http://id.webbrick.co.uk/events/time/isDark&amp;state=0"
                            >
                        Do Sunrise
                    </wb:simpleButton>
                </td>
                <td>
                    <wb:simpleButton 
                            wbTarget="/sendevent/time/isDark?type=http://id.webbrick.co.uk/events/time/isDark&amp;state=1"
                            >
                        Do Sunset
                    </wb:simpleButton>
                </td>
            </tr>
            <tr>
                <th>&nbsp;</th>
            </tr>
            <tr>
                <td>
                    <wb:simpleButton
                            wbTarget="/sendevent/dayphase/morning"
                            >
                        Do Morning
                    </wb:simpleButton>
                </td>
                <td>
                    <wb:simpleButton 
                            wbTarget="/sendevent/dayphase/day"
                            >
                        Do Day
                    </wb:simpleButton>
                </td>
                <td>
                    <wb:simpleButton 
                            wbTarget="/sendevent/dayphase/evening"
                            >
                        Do Evening
                    </wb:simpleButton>
                </td>
            </tr>
            <tr>
                <td>
                    <wb:simpleButton
                            wbTarget="/sendevent/dayphase/night"
                            >
                        Do Night
                    </wb:simpleButton>
                </td>
            </tr>
        </table>
    </div>

    <div py:match="item.tag=='{http://id.webbrick.co.uk/}botboxcontent'" id="botboxcontent">
        <!-- !Insert content for bottom right box in here -->
        ${output_functional_links( "", "", [True,True,True,True,True] )}
    </div>

</html>

