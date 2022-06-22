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

namespace Image_comparer_test_project__.net_framework_
{
    internal class Comparer
    {
        private SectorData firstImgSectors;
        private SectorData[] SecondimgListSectors = new SectorData[1];
        private DataSet ds = new DataSet();
        private List<Results> results;
        private string[] fileNames = new string[1];

        //only square supported for now
        private const int WidthSectors = 17;
        private const int HeightSectors = 17;

        public static void Main()
        {
            TcpClient client;
            TcpListener server = new TcpListener(IPAddress.Parse("192.168.1.200"), 5053);

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

        private void Prepimage(string filename, bool firstImg, int secondImagePos)
        {
            Bitmap image = (Bitmap)Image.FromFile(filename);

            double ratio = image.Height * 1.0 / image.Width;
            image = CropAtRect(image, new Rectangle(0, 0, 200, (int)(200 * ratio)));

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
            for (int a = 0, b = 0; a < rgbValues.Length; a += 3, b++)
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

        private void ThreadRunPrep(string[] filenames, int startPos)
        {
            for (int a = 0; a < filenames.Length; a++)
            {
                Prepimage(filenames[a], false, startPos + a);
            }
        }

        private void ThreadRunCompare(int startPos, int length, SectorData firstimage)
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

        private Results CompareImg(SectorData firstImgSectorsCompare, SectorData secondImgSectorsCompare, int pos)
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
}
