using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Net;
using System.Net.Sockets;

namespace Image_comparer_test_project__.net_framework_
{
    internal class TCP_server
    {
        public static void Main()
        {
            TcpClient client;
            TcpListener server = new TcpListener(IPAddress.Parse("192.168.1.5"), 5053);

            server.Start();
            Byte[] bytes = new Byte[128];
            string data = null;

            while (true)
            {
                Console.Write("Waiting for a connection... ");

                client = server.AcceptTcpClient();
                Console.WriteLine("Connected!");

                data = null;
                NetworkStream stream = client.GetStream();

                int i;
                while ((i = stream.Read(bytes, 0, bytes.Length)) != 0)
                {
                    data = Encoding.ASCII.GetString(bytes, 0, i);
                    Console.WriteLine("Received: {0}", data);
                    data = data.ToUpper();
                    byte[] msg = Encoding.ASCII.GetBytes(data);
                    stream.Write(msg, 0, msg.Length);
                    Console.WriteLine("Sent: {0}", data);
                }                
            }
            //client.Close();
        }
    }
}
