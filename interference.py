#!/usr/bin/python
# coding: utf-8

__author__ = "Luca Tartarini"
__license__ = "GPL"
__email__ = "ltartarini90@gmail.com"
__date__ = "23/04/2015"

import os, random, sys
import mininet.net
import mininet.node
import mininet.cli
import mininet.log
import mininet.ns3
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.util import dumpNodeConnections  
from mininet.ns3 import *

import ns.core
import ns.network
import ns.wifi
import ns.csma
import ns.wimax
import ns.uan
import ns.netanim

# Maximum number of wifi channels
maxChannelNumber = 11

# Netanim nodes color
switch_color = (255, 255, 255) # white
server_color = (255, 0, 0) # red
mobile_node_color = (0, 0, 255) # blue
access_point_color = (0, 255, 0) # green

def Network(argv):
    
    cmd = ns.core.CommandLine()
    
    cmd.tcp = None
    cmd.AddValue("tcp", "iperf bandwidth")
    
    cmd.udp = None
    cmd.AddValue("udp", "iperf jitter and packet loss")  
    
    cmd.json = None
    cmd.AddValue("json", "iper3 in JSON format")
    
    cmd.distance = None
    cmd.AddValue("distance", "set distance between routers")
    
    cmd.Parse(argv)
       
    if cmd.distance is not None:
        distance = float(cmd.distance)
        
    setLogLevel( 'info' )

    info( "*** Create an Wifi network and add nodes to it\n" )
    net = Mininet(controller=RemoteController, link=CSMALink)

    info( '*** Adding controller\n' )
    net.addController('c0', ip='127.0.0.1', port=6633)
    
    info( "*** Creating mobility models\n" )
    """ Constant position """
    mobilityHelper1 = ns.mobility.MobilityHelper()
    mobilityHelper1.SetMobilityModel("ns3::ConstantPositionMobilityModel")
   
    """ Random walk """
    mobilityHelper2 = ns.mobility.MobilityHelper()
    mobilityHelper2.SetMobilityModel("ns3::RandomWalk2dMobilityModel")
        
    info( "*** Creating swtich\n" )
    s0 = net.addSwitch('s0', listenPort=6634) 
    
    info( "*** Creating server node h0\n" )
    h0 = net.addHost('h0', mac='aa:aa:aa:aa:aa:01', ip="10.0.1.100/24")
    
    info( "*** Creating mobile node h1\n" )
    h1 = net.addHost('h1', mac='aa:aa:aa:aa:aa:02', ip="10.0.2.100/24")
    
    info( "*** Creating mobile node h2\n" )
    h2 = net.addHost('h2', mac='aa:aa:aa:aa:aa:03', ip="10.0.3.100/24")
    
    info( "*** Creating access point h3\n" )
    h3 = net.addHost('h3', mac='aa:aa:aa:aa:aa:04', ip="10.0.1.1")
    
    info( "*** Creating access point h4\n" )
    h4 = net.addHost('h4', mac='aa:aa:aa:aa:aa:05', ip="10.0.1.2")

    info( "*** Adding wired links\n" )
    csma0 = CSMALink(s0, h0, DataRate="10Mbps", Delay="1ms") 
    csma1 = CSMALink(s0, h3, DataRate="10Mbps", Delay="1ms")
    csma2 = CSMALink(s0, h4, DataRate="10Mbps", Delay="1ms")
    
    info( "*** Adding wireless links\n" ) 
    wifi1_channelNumber = 1
    wifi2_channelNumber = 11     

    wifiChannelHelper = ns.wifi.YansWifiChannelHelper.Default()
    wifiChannel = wifiChannelHelper.Create()
    wifiPhy1 = ns.wifi.YansWifiPhyHelper.Default()
    wifiPhy2 = ns.wifi.YansWifiPhyHelper.Default()

    wifi1 = WIFISegment()
    wifi2 = WIFISegment()
    
    wifi1.channel = wifiChannel
    wifi1.phyhelper = wifiPhy1
    if wifi1_channelNumber <= 0 or wifi1_channelNumber > maxChannelNumber: 
        wifi1_channelNumber = random.randint(1, maxChannelNumber)
        warn("illegal channel number, choose a random channel number %s.\n", 
             wifi1_channelNumber)
    else:
        wifiPhy1.Set("ChannelNumber", ns.core.UintegerValue(wifi1_channelNumber))
    
    wifi2.channel = wifiChannel
    wifi2.phyhelper = wifiPhy2
    if wifi2_channelNumber <= 0 or wifi2_channelNumber > maxChannelNumber: 
        wifi2_channelNumber = random.randint(1, maxChannelNumber)
        warn("illegal channel number, choose a random channel number %s.\n", 
             wifi2_channelNumber)
    else:
        wifiPhy2.Set("ChannelNumber", ns.core.UintegerValue(wifi2_channelNumber))
        
    # same YansWifiPhyHelper for the 2 WifiAPs for interference
    wifiPhy1.SetChannel(wifiChannel)
    wifiPhy2.SetChannel(wifiChannel)
    
    tb_h3 = wifi1.addAp(h3, ssid='ssid1')
    tb_h1 = wifi1.addSta(h1, ssid='ssid1')
    tb_h4 = wifi2.addAp(h4, ssid='ssid2')
    tb_h2 = wifi2.addSta(h2, ssid='ssid2')

    """ Set IPs for access points """
    h3.setIP('10.0.2.1', intf='h3-eth1')
    h4.setIP('10.0.3.1', intf='h4-eth1')
    
    # set mobility model (before setting positions !!!)
    info("*** Mobility models\n")
    mininet.ns3.setMobilityModel(s0, mobilityHelper1)
    print mininet.ns3.getMobilityModel(s0)
    mininet.ns3.setMobilityModel(h0, mobilityHelper1)
    print mininet.ns3.getMobilityModel(h0)
    mininet.ns3.setMobilityModel(h1, mobilityHelper1)
    print mininet.ns3.getMobilityModel(h1)
    mininet.ns3.setMobilityModel(h2, mobilityHelper1)
    print mininet.ns3.getMobilityModel(h2)
    mininet.ns3.setMobilityModel(h3, mobilityHelper1)
    print mininet.ns3.getMobilityModel(h3)
    mininet.ns3.setMobilityModel(h4, mobilityHelper1)
    print mininet.ns3.getMobilityModel(h4)
    
    y_h3 = -distance/2
    y_h4 = distance/2
    
    # set position (after wifi.addAp/Sta() otherwise node position become 0.0,0.0)
    info("*** Positions\n") 
    mininet.ns3.setPosition(s0, -3.0, 0.0, 0.0)
    print mininet.ns3.getPosition(s0)
    mininet.ns3.setPosition(h0, -5.0, 0.0, 0.0)
    print mininet.ns3.getPosition(h0)
    mininet.ns3.setPosition(h1, 1.5, -1.5, 0.0)
    print mininet.ns3.getPosition(h1)
    mininet.ns3.setPosition(h2, 1.5, 1.5, 0.0)
    print mininet.ns3.getPosition(h2)
    mininet.ns3.setPosition(h3, 0.0, y_h3, 0.0)
    print mininet.ns3.getPosition(h3)
    mininet.ns3.setPosition(h4, 0.0, y_h4, 0.0)
    print mininet.ns3.getPosition(h4)
    
    """
    # Wireshark files
    rv = os.path.isdir("/tmp/pcap/interference_scenario")
    if rv is False:
        os.mkdir("/tmp/pcap/interference_scenario")
    ns.wifi.YansWifiPhyHelper().Default().EnablePcapAll("/tmp/pcap/wifi")
    ns.csma.CsmaHelper().EnablePcapAll("/tmp/pcap/csma")
    """
    """ NetAnim configuration """
    rv = os.path.isdir("/tmp/xml")
    if rv is False:
        os.mkdir("/tmp/xml")    
    anim = ns.netanim.AnimationInterface("/tmp/xml/interference_scenario.xml")
    anim.EnablePacketMetadata(True)

    anim.UpdateNodeDescription(s0.nsNode, 's0 - switch '+str(s0.nsNode.GetId()))
    anim.UpdateNodeColor(s0.nsNode, switch_color[0], switch_color[1], switch_color[2])
        
    anim.UpdateNodeDescription(h0.nsNode, 'h0 - server node ' + str(h0.nsNode.GetId()))
    anim.UpdateNodeColor(h0.nsNode, server_color[0], server_color[1], server_color[2]) 
    
    anim.UpdateNodeDescription(h1.nsNode, 'h1 - mobile node ' + str(h1.nsNode.GetId()))
    anim.UpdateNodeColor(h1.nsNode, mobile_node_color[0], mobile_node_color[1], mobile_node_color[2]) 

    anim.UpdateNodeDescription(h2.nsNode, 'h2 - mobile node ' + str(h2.nsNode.GetId()))
    anim.UpdateNodeColor(h2.nsNode, mobile_node_color[0], mobile_node_color[1], mobile_node_color[2])
    
    anim.UpdateNodeDescription(h3.nsNode, 'h3 - access point ' + str(h3.nsNode.GetId()))
    anim.UpdateNodeColor(h3.nsNode, access_point_color[0], access_point_color[1], access_point_color[2]) 
    
    anim.UpdateNodeDescription(h4.nsNode, 'h4 - access point ' + str(h4.nsNode.GetId()))
    anim.UpdateNodeColor(h4.nsNode, access_point_color[0], access_point_color[1], access_point_color[2])  

    info( '*** Starting network\n' )
    net.start()

    mininet.ns3.start()  
    
    """ Adding route entries """
    h0.cmd('route add -net 10.0.2.0 netmask 255.255.255.0 gw 10.0.1.1 dev h0-eth0')
    h0.cmd('route add -net 10.0.3.0 netmask 255.255.255.0 gw 10.0.1.2 dev h0-eth0')
    
    h1.cmd('route add default gw 10.0.2.1')
    h2.cmd('route add default gw 10.0.3.1')
    
    h3.cmd('route add -net 10.0.2.0 netmask 255.255.255.0 dev h3-eth1')
    h3.cmd('route add -net 10.0.3.0 netmask 255.255.255.0 gw 10.0.1.2 dev h3-eth0')
    
    h4.cmd('route add -net 10.0.3.0 netmask 255.255.255.0 dev h4-eth1')
    h4.cmd('route add -net 10.0.2.0 netmask 255.255.255.0 gw 10.0.1.1 dev h4-eth0')
    
    print "*** Dumping host connections"
    dumpNodeConnections(net.hosts)

    """ static measurements """
    # h1, h2 -> h0
    if cmd.udp is not None:
        if cmd.json is not None:
            h2.cmdPrint('ping 10.0.1.100 -c 30 > /home/luca/ping_h2_h0_udp &')
            h0.cmdPrint('iperf3 -s -p 5003 -i 1 -J > /home/luca/iperf_interference_h0_server_h1_client_udp.json &')
            #h0.cmdPrint('iperf3 -s -p 5004 -i 1 > /home/luca/iperf_interference_h0_server_h2_client &')
            h1.cmdPrint('iperf3 -c 10.0.1.100 -u -b 2M -p 5003 -n 5M -J > /home/luca/iperf_interference_h1_client_udp.json &')
            #h2.cmdPrint('iperf3 -c 10.0.1.100 -u -b 2M -p 5004 -n 5M > /home/luca/iperf_interference_h2_client &')
        else:
            """
            h2.cmdPrint('ping 10.0.1.100 -c 30 > /home/luca/stats/interference_scenario/ping_h2_h0_udp &')
            #h1.cmdPrint('ping 10.0.1.100 -c 30 > /home/luca/ping_h1_h0_udp &')
            h0.cmdPrint('iperf3 -s -p 5003 -i 1 > /home/luca/stats/interference_scenario/iperf_interference_h0_server_h1_client_udp &')
            #h0.cmdPrint('iperf3 -s -p 5004 -i 1 > /home/luca/iperf_interference_h0_server_h2_client &')
            h1.cmdPrint('iperf3 -c 10.0.1.100 -u -b 2M -p 5003 -n 5M > /home/luca/stats/interference_scenario/iperf_interference_h1_client_udp &')
            #h2.cmdPrint('iperf3 -c 10.0.1.100 -u -b 2M -p 5004 -n 5M > /home/luca/iperf_interference_h2_client &')
            """
            h2.cmdPrint('ping 10.0.1.100 -c 100 -i 0.5 > /home/luca/stats/interference_scenario/ping_h2_h0_udp_'+str(distance)+' &')
            src1, src2, dst = net.hosts[1], net.hosts[2], net.hosts[0]
            net.iperf([src1, dst], l4Type='UDP', udpBw='2M', seconds=55)

    if cmd.tcp is not None:  
        if cmd.json is not None:
            h2.cmdPrint('ping 10.0.1.100 -c 30 > /home/luca/ping_h2_h0_tcp &')
            h0.cmdPrint('iperf3 -s -p 5003 -i 1 -J > /home/luca/iperf_interference_h0_server_h1_client_tcp.json &')
            h1.cmdPrint('iperf3 -c 10.0.1.100 -p 5003 -J > /home/luca/iperf_interference_h1_client_tcp.json &') 
        else:
            h2.cmdPrint('ping 10.0.1.100 -c 30 -i 0.5 > /home/luca/ping_h2_h0_tcp &')
            h0.cmdPrint('iperf3 -s -p 5003 -i 1 > /home/luca/iperf_interference_h0_server_h1_client_tcp &')
            h1.cmdPrint('iperf3 -c 10.0.1.100 -p 5003 > /home/luca/iperf_interference_h1_client_tcp &')

    # h0 -> h1, h2
    #h1.cmdPrint('iperf3 -s -p 5003 -i 1 > /home/luca/iperf_interference_h0_server_h1_client &')
    #h2.cmdPrint('iperf3 -s -p 5003 -i 1 > /home/luca/iperf_interference_h0_server_h2_client &')
    #h0.cmdPrint('iperf3 -c 10.0.2.100 -u -b 2M -p 5003 -n 5M > /home/luca/iperf_interference_h1_client &')
    #h0.cmdPrint('iperf3 -c 10.0.3.100 -u -b 2M -p 5003 -n 5M > /home/luca/iperf_interference_h2_client &')
    
    # h3 -> h0
    #h0.cmdPrint( 'iperf3 -s -p 5003 -i 1 -J > /home/luca/iperf_static_h0_server.json &' )
    #h3.cmdPrint( 'iperf3 -c 192.168.0.1 -u -b 3M -p 5003 -J > /home/luca/iperf_static_h3_client.json &' )
    
    # h0 -> h1
    #h1.cmdPrint( 'iperf3 -s -p 5003 -i 1 -J > /home/luca/iperf_static_h1_server.json &' )
    #h0.cmdPrint( 'iperf3 -c 192.168.0.2 -u -b 3M -p 5003 -J > /home/luca/iperf_static_h0_client.json &' )
    
    # h1 -> h2
    #h2.cmdPrint( 'iperf3 -s -p 5003 -i 1 -J > /home/luca/iperf_static_h2_server.json &' )
    #h1.cmdPrint( 'iperf3 -c 192.168.0.3 -u -b 3M -p 5003 -J > /home/luca/iperf_static_h1_client.json &' )
   
    
    info( 'Testing network connectivity\n' )
    #net.pingAll()
    
    """
    src, dst = net.hosts[0], net.hosts[2]
    packet_loss_perc = net.ping([src, dst], timeout)
    src, dst = net.hosts[0], net.hosts[2]
    bandwidth = net.iperf([src, dst], seconds=5)
    """
 
    #CLI(net)    
    
    info( '*** Stopping network\n' )
    mininet.ns3.stop()
    info( '*** mininet.ns3.stop()\n' )
    mininet.ns3.clear()
    info( '*** mininet.ns3.clear()\n' )
    net.stop()
    info( '*** net.stop()\n' )
    
if __name__ == '__main__':
    setLogLevel( 'info' )
    Network(sys.argv)
    sys.exit(0)
