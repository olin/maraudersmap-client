//Adapted from Managed Wifi example by Cory Dolphin
//Outputs Wireless Signal Strengths in JSON format, an array with many objects as described below:
//EXAMPLE: [{"SSID":"OLIN_GUEST","BSSID":"00:15:E8:E3:DF","RSSI":"-78"}]


using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Text;
using NativeWifi;

class Program
{

    static void Main(string[] args)
    {
        WlanClient client = new WlanClient();
        try
        {
            foreach (WlanClient.WlanInterface wlanIface in client.Interfaces)
            {
                Wlan.WlanBssEntry[] wlanBssEntries = wlanIface.GetNetworkBssList();
                List<string> wirelessData = new List<string>();
                foreach (Wlan.WlanBssEntry network in wlanBssEntries)
                {
                    int rss = network.rssi;
                    byte[] macAddrBytes = network.dot11Bssid;

                    string tMac = "";
                    for (int i = 0; i < macAddrBytes.Length; i++){
                        tMac += macAddrBytes[i].ToString("x2").PadLeft(2, '0').ToUpper();
                    }

                    string macAddress = "";
                    for (int i = 0; i < (tMac.Length / 2); i++)
                    {
                        macAddress += tMac.Substring(i * 2, 2);//note C# substring(i,j) goes from i to i+j
                        if (i != 5) { macAddress += ":"; }
                    }

                    string ssid = System.Text.ASCIIEncoding.ASCII.GetString(network.dot11Ssid.SSID).ToString().Replace(((char)0) + "", ""); //replace null chars
                    string dataString = "\"SSID\":\"" + ssid + "\",\"BSSID\":\"" + macAddress + "\",\"RSSI\":\"" + rss.ToString() + "\"";
                    wirelessData.Add(dataString);
                }
                Console.Write("[");

                int iter = 0;
                int numValues = wirelessData.Count;
                foreach (String row in wirelessData)
                {
                    Console.Write("{" + String.Join("},{", row+ "}")); //TODO: more elegant solution for JSON

                    if (iter + 1 < numValues)
                    {
                        Console.Write(",");
                    }
                    iter++;
                }
                Console.Write("]");
            }
            
        }
        catch (Exception ex)
        {
            //lala
        }

    }
}
