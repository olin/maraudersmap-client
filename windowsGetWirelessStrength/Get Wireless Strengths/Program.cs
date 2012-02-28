//Adapted from Managed Wifi example by Cory Dolphin

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
                Dictionary<string, List<String>> dictionary = new Dictionary<string, List<String>>();
                foreach (Wlan.WlanBssEntry network in wlanBssEntries)
                {
                    int rss = network.rssi;
                    byte[] macAddrBytes = network.dot11Bssid;

                    string tMac = "";
                    for (int i = 0; i < macAddrBytes.Length; i++){
                        tMac += macAddrBytes[i].ToString("x2").PadLeft(2, '0').ToUpper();
                    }

                    string macAddress = "";
                    for (int i = 1; i < (tMac.Length / 2); i++)
                    {
                        macAddress += tMac.Substring((i - 1) * 2, 2);//note C# substring(i,j) goes from i to i+j
                        if (i != 5) { macAddress += ":"; }
                    }

                    string ssid = System.Text.ASCIIEncoding.ASCII.GetString(network.dot11Ssid.SSID).ToString().Replace(((char)0) + "", ""); //replace null chars
                    string dataString = "\"MAC\":\"" + macAddress + "\",\"Signal\":\"" + network.linkQuality + "\",\"RSSI\":\"" + rss.ToString() + "\"";
                    if (dictionary.ContainsKey(ssid))
                    {
                        dictionary[ssid].Add(dataString);
                    }
                    else
                    {
                        //there must be a more efficient/ better pattern in C#? Literal lists are not a thing...
                        List<String> tList = new List<String>();
                        tList.Add(dataString);
                        dictionary.Add(ssid,tList);
                    }
                }
                Console.Write("{");
                foreach (String ssid in dictionary.Keys)
                {
                    Console.Write("\"" + ssid + "\"" + ":[{" + String.Join("},{",dictionary[ssid]) + "}],"); //TODO: more elegant solution for JSON
                }
                Console.Write("}");
            }
            
        }
        catch (Exception ex)
        {
            //lala
        }

    }
}
