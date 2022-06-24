using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Threading;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using Newtonsoft.Json;

namespace Image_comparer_test_project__.net_framework_
{
    internal class Comparer
    {
        private static SectorData firstImgSectors;
        private static SectorData[] SecondimgListSectors = new SectorData[1];
        private static List<Results> results = new List<Results>();
        private static string[] fileNames = new string[1];

        //only square supported for now
        private const int WidthSectors = 17;
        private const int HeightSectors = 17;

        public static void Main()
        {
            System.Diagnostics.Process.GetCurrentProcess().PriorityClass = System.Diagnostics.ProcessPriorityClass.High;
            TcpClient client;
            TcpListener server = new TcpListener(IPAddress.Parse("192.168.1.200"), 5053);

            server.Start();
            Byte[] bytes = new Byte[250000];
            string data = null;

            ImageConverter imageConverter = new ImageConverter();

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
                    Message message = JsonConvert.DeserializeObject<Message>(data);
                    byte[] imgBytes = Convert.FromBase64String(message.content);

                    Bitmap bm = (Bitmap)imageConverter.ConvertFrom(imgBytes);
                    bm.Save("temp.png", ImageFormat.Png);
                    Prepimage("temp.png", true, 0);
                    fileNames = Directory.GetFiles(@"../../../../../Dataset/" + message.class_name);

                    SecondimgListSectors = new SectorData[fileNames.Length];
                    Thread[] threads = new Thread[30];

                    for (int a = 0; a < threads.Length; a++)
                    {
                        string[] substring = new string[fileNames.Length / threads.Length];
                        int subStringLength = substring.Length * a;
                        Array.Copy(fileNames, subStringLength, substring, 0, substring.Length);
                        threads[a] = new Thread(() => ThreadRunPrep(substring, subStringLength));
                        threads[a].Start();
                    }

                    string[] lastSubString = new string[fileNames.Length % threads.Length];
                    Array.Copy(fileNames, fileNames.Length - fileNames.Length % threads.Length, lastSubString, 0, lastSubString.Length);
                    Thread lastThread = new Thread(() => ThreadRunPrep(lastSubString, fileNames.Length - fileNames.Length % threads.Length));
                    lastThread.Start();

                    foreach (var thread in threads)
                    {
                        thread.Join();
                    }

                    lastThread.Join();

                    threads = new Thread[25];
                    SectorData firstimage = firstImgSectors;
                    int length = SecondimgListSectors.Length / threads.Length;
                    for (int a = 0; a < threads.Length; a++)
                    {
                        int startPos = length * a;
                        threads[a] = new Thread(() => ThreadRunCompare(startPos, length, firstimage));
                        threads[a].Start();
                    }

                    lastThread = new Thread(() => ThreadRunCompare(0, 0, firstimage));
                    if (SecondimgListSectors.Length % threads.Length != 0)
                    {
                        length = SecondimgListSectors.Length % threads.Length;
                        int lastPos = SecondimgListSectors.Length - length;
                        lastThread = new Thread(() => ThreadRunCompare(lastPos, length, firstimage));
                        lastThread.Start();
                    }

                    foreach (var thread in threads)
                    {
                        thread.Join();
                    }

                    if (SecondimgListSectors.Length % threads.Length != 0)
                    {
                        lastThread.Join();
                    }

                    List<Tuple<double, string>> totalDiff = new List<Tuple<double, string>>();
                    for (int a = 0; a < results.Count; a++)
                    {
                        totalDiff.Add(Tuple.Create((Convert.ToDouble(results[a].HueDiffPercent.Replace("%", "")) +
                            Convert.ToDouble(results[a].BrightnessDiffPercent.Replace("%", "")) +
                            Convert.ToDouble(results[a].SaturationDiffPercent.Replace("%", ""))) / 3, results[a].FileName));
                    }

                    totalDiff = totalDiff.OrderBy(x => x.Item1).ToList();

                    Message newMSG = new Message{
                        class_name = message.class_name,
                        complex_case = message.complex_case,
                        user_index = message.user_index
                    };

                    for (int b = 0; b < 20; b++)
                    {
                        if (b == 19)
                        {
                            newMSG.content += totalDiff[b].Item2 + "-" + (100 - Convert.ToInt32(totalDiff[b].Item1));
                            break;
                        }
                        newMSG.content += totalDiff[b].Item2 + "-" + (100 - Convert.ToInt32(totalDiff[b].Item1)) + "_";
                    }

                    string msgJSON = JsonConvert.SerializeObject(newMSG);
                    byte[] msg = Encoding.ASCII.GetBytes(msgJSON);
                    Array.Resize(ref msg, 250000);
                    stream.Write(msg, 0, msg.Length);
                }
            }
        }

        private static Bitmap CropAtRect(Bitmap b, Rectangle r)
        {
            Bitmap nb = new Bitmap(r.Width, r.Height, PixelFormat.Format24bppRgb);
            Graphics g = Graphics.FromImage(nb);
            g.DrawImage(b, r.X, r.Y, nb.Width, nb.Height);
            return nb;
        }

        private static UInt16 ToUInt16(int number)
        {
            if (number < 0) return (UInt16)(-number);
            return (UInt16)number;
        }

        private static void Prepimage(string filename, bool firstImg, int secondImagePos)
        {
            Bitmap image = (Bitmap)Image.FromFile(filename);

            //double ratio = image.Height * 1.0 / image.Width;
            //image = CropAtRect(image, new Rectangle(0, 0, 200, (int)(200 * ratio)));

            SectorData sectorAverages = new SectorData
            {
                HSVData = new List<(int, int, int)>(),
                FileName = filename.Substring(filename.LastIndexOf(@"\") + 1),
            };

            int imageWidth = image.Width;
            int sectorWidth = image.Width / WidthSectors;
            int sectorheight = image.Height / HeightSectors;
            int totalPixelsPerSector = sectorWidth * sectorheight;
            int lastWidthSector = image.Width % WidthSectors;
            int lastheightSector = image.Height % HeightSectors;

            BitmapData bmpData =
                image.LockBits(new Rectangle(0, 0, image.Width, image.Height), ImageLockMode.ReadWrite,
                image.PixelFormat);

            IntPtr ptr = bmpData.Scan0;

            int bytes = Math.Abs(bmpData.Stride) * image.Height;
            byte[] rgbValues = new byte[bytes];

            Marshal.Copy(ptr, rgbValues, 0, bytes);

            var t = Task.Run(() => {
                image.UnlockBits(bmpData);
                bmpData = null;
            });

            Span<(int, int, int)> colors = new (int, int, int)[bytes / 3];
            for (int a = 0, b = 0; a < rgbValues.Length - 2; a += 3, b++)
            {
                float red = rgbValues[a + 2] / 255f;
                float green = rgbValues[a + 1] / 255f;
                float blue = rgbValues[a + 0] / 255f;
                float hue = 0f;
                int brightness = 0;
                int saturation = 0;
                float max = red >= green ? red >= blue ? red : blue >= green ? blue : green : blue >= green ? blue : green;
                float min = red < green ? red < blue ? red : blue < green ? blue : green : blue < green ? blue : green;
                float diff = max - min;

                if (max == min)
                {
                    hue = 0;
                }
                else if (max == red)
                {
                    hue = (green - blue) / (max - min);

                }
                else if (max == green)
                {
                    hue = 2f + (blue - red) / (max - min);

                }
                else
                {
                    hue = 4f + (red - green) / (max - min);
                }

                hue *= 60;
                if (hue < 0) hue += 360;

                brightness = (int)(max * 100.0);

                if (max == 0)
                {
                    saturation = 0;
                }
                else
                {
                    saturation = (int)(diff / max * 100.0);
                }

                colors[b] = ((int)hue, brightness, saturation);
            }

            for (int a = 0; a < WidthSectors; a++)
            {
                for (int b = 0; b < HeightSectors; b++)
                {
                    int TotalHueValues = 0;
                    int totalBrightnessValues = 0;
                    int totalSaturationValues = 0;

                    double weight = 1;

                    if ((WidthSectors / 2 - ToUInt16(WidthSectors / 2 - a)) < (WidthSectors / 2 - ToUInt16(WidthSectors / 2 - b)))
                    {
                        weight = 0.08 * (WidthSectors / 2 - ToUInt16(WidthSectors / 2 - a)) + 1;

                    }
                    else
                    {
                        weight = 0.08 * (WidthSectors / 2 - ToUInt16(WidthSectors / 2 - b)) + 1;
                    }

                    for (int c = 0; c < sectorheight; c++)
                    {
                        for (int d = 0; d < sectorWidth; d++)
                        {
                            int pos = (b * sectorheight + c) * imageWidth + a * sectorWidth + d;
                            TotalHueValues += colors[pos].Item1;
                            totalBrightnessValues += colors[pos].Item2;
                            totalSaturationValues += colors[pos].Item3;
                        }
                    }

                    sectorAverages.HSVData.Add(((int)(TotalHueValues / totalPixelsPerSector * weight),
                        (int)(totalBrightnessValues / totalPixelsPerSector * weight), (int)(totalSaturationValues / totalPixelsPerSector * weight)));
                }
            }

            colors = null;

            if (firstImg)
            {
                firstImgSectors = sectorAverages;
                return;
            }
            SecondimgListSectors[secondImagePos] = sectorAverages;
        }

        private static void ThreadRunPrep(string[] filenames, int startPos)
        {
            for (int a = 0; a < filenames.Length; a++)
            {
                Prepimage(filenames[a], false, startPos + a);
            }
        }

        private static void ThreadRunCompare(int startPos, int length, SectorData firstimage)
        {
            Results[] resultsTemp = new Results[length];

            for (int a = startPos, b = 0; a < startPos + length; a++, b++)
            {
                resultsTemp[b] = CompareImg(firstimage, SecondimgListSectors[a], a);
            }

            lock (results)
            {
                results.AddRange(resultsTemp);
            }
        }

        private static Results CompareImg(SectorData firstImgSectorsCompare, SectorData secondImgSectorsCompare, int pos)
        {
            List<int> diffHue = new List<int>();
            List<int> diffBrightness = new List<int>();
            List<int> diffSaturation = new List<int>();
            List<int> diffTotal = new List<int>();

            firstImgSectorsCompare.HSVData = firstImgSectorsCompare.HSVData.OrderBy(x => x.Item1).ToList();
            secondImgSectorsCompare.HSVData = secondImgSectorsCompare.HSVData.OrderBy(x => x.Item1).ToList();

            for (int a = 0; a < firstImgSectorsCompare.HSVData.Count; a++)
            {
                diffHue.Add(ToUInt16(firstImgSectorsCompare.HSVData[a].Item1 - secondImgSectorsCompare.HSVData[a].Item1));
            }

            for (int a = 0; a < firstImgSectorsCompare.HSVData.Count; a++)
            {
                diffBrightness.Add(ToUInt16(firstImgSectorsCompare.HSVData[a].Item2 - secondImgSectorsCompare.HSVData[a].Item2));
            }

            for (int a = 0; a < firstImgSectorsCompare.HSVData.Count; a++)
            {
                diffSaturation.Add(ToUInt16(firstImgSectorsCompare.HSVData[a].Item3 - secondImgSectorsCompare.HSVData[a].Item3));
            }

            string HueDiffPercent = (diffHue.Average() / (diffHue.Max() / 100.0)).ToString();
            string BrightnessDiffPercent = (diffBrightness.Average() / (diffBrightness.Max() / 100.0)).ToString();
            string SaturationDiffPercent = (diffSaturation.Average() / (diffSaturation.Max() / 100.0)).ToString();
            return new Results
            {
                HueDifference = (int)diffHue.Average(),
                BrightnessDifference = (int)diffBrightness.Average(),
                SaturationDifference = (int)diffSaturation.Average(),
                HueDiffPercent = HueDiffPercent == "NaN" ? "0%" : HueDiffPercent + "%",
                BrightnessDiffPercent = BrightnessDiffPercent == "NaN" ? "0%" : BrightnessDiffPercent + "%",
                SaturationDiffPercent = SaturationDiffPercent == "NaN" ? "0%" : SaturationDiffPercent + "%",
                FileName = secondImgSectorsCompare.FileName,
            };
        }
    }

    internal struct Message
    {
        public string user_index { get; set; }

        public string content { get; set; }

        public string complex_case { get; set; }
        
        public string class_name { get; set; }
    }
}
