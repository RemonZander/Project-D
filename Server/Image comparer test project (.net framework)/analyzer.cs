using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Threading;
using System.IO;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;

namespace Image_comparer_test_project__.net_framework_
{
    internal sealed partial class Form1 : Form
    {
        private SectorData firstImgSectors;
        private SectorData[] SecondimgListSectors = new SectorData[1];
        private DataSet ds = new DataSet();
        private List<Results> results;
        private string[] fileNames = new string[1];

        //only square supported for now
        private const int WidthSectors = 17;
        private const int HeightSectors = 17;

        private PixelWeights PixelWeights = PixelWeights.Geen;

        private Modes mode = Modes.Single;

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
            Bitmap image = (Bitmap)Bitmap.FromFile(filename);

            double ratio = image.Height * 1.0 / image.Width;
            image = CropAtRect(image, new Rectangle(0, 0, 200, (int)(200 * ratio)));

            //for data analysis only
            Bitmap nb = new Bitmap(image.Width, image.Height);
            Graphics g = Graphics.FromImage(nb);

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
                //float min2 = Math.Min(Math.Min(red, green), blue);
                //float max2 = Math.Max(Math.Max(red, green), blue);
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

                    switch (PixelWeights)
                    {
                        case PixelWeights.Logaritmisch:
                            if (a == 0 || b == 0)
                            {
                                weight = 1;
                            }
                            if ((WidthSectors / 2 - ToUInt16(WidthSectors / 2 - a)) < (WidthSectors / 2 - ToUInt16(WidthSectors / 2 - b)))
                            {
                                weight = Math.Log(a) * a + 1.0;

                            }
                            else
                            {
                                weight = Math.Log(b) * a + 1.0;
                            }
                            break;
                        case PixelWeights.Linear:
                            if ((WidthSectors / 2 - ToUInt16(WidthSectors / 2 - a)) < (WidthSectors / 2 - ToUInt16(WidthSectors / 2 - b)))
                            {
                                weight = 0.08 * (WidthSectors / 2 - ToUInt16(WidthSectors / 2 - a)) + 1;

                            }
                            else
                            {
                                weight = 0.08 * (WidthSectors / 2 - ToUInt16(WidthSectors / 2 - b)) + 1;
                            }
                            break;
                        case PixelWeights.Vierkant:
                            if ((WidthSectors / 2 - ToUInt16(WidthSectors / 2 - a)) < (WidthSectors / 2 - ToUInt16(WidthSectors / 2 - b)))
                            {
                                weight = 2.0 * (WidthSectors / 2 - ToUInt16(WidthSectors / 2 - a)) + 1;

                            }
                            else
                            {
                                weight = 2.0 * (WidthSectors / 2 - ToUInt16(WidthSectors / 2 - b)) + 1;
                            }
                            break;
                        case PixelWeights.Exponentieel:
                            if ((WidthSectors / 2 - ToUInt16(WidthSectors / 2 - a)) < (WidthSectors / 2 - ToUInt16(WidthSectors / 2 - b)))
                            {
                                weight = a * (WidthSectors / 2 - ToUInt16(WidthSectors / 2 - a)) + 1;

                            }
                            else
                            {
                                weight = b * (WidthSectors / 2 - ToUInt16(WidthSectors / 2 - b)) + 1;
                            }
                            break;
                        default:
                            break;
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
                    //for data analysis only
                    g.FillRectangle(new SolidBrush(ColorFromHSV(TotalHueValues / totalPixelsPerSector, totalSaturationValues / totalPixelsPerSector / 100.0, totalBrightnessValues / totalPixelsPerSector / 100.0)),
                        new Rectangle(sectorWidth * a, sectorheight * b, sectorWidth, sectorheight));

                    sectorAverages.HSVData.Add(((int)(TotalHueValues / totalPixelsPerSector * weight), (int)(totalBrightnessValues / totalPixelsPerSector * weight), (int)(totalSaturationValues / totalPixelsPerSector * weight)));
                }
            }

            colors = null;
            nb.Save(Environment.GetFolderPath(Environment.SpecialFolder.Desktop) + @"\resultaten\prep\" + filename.Substring(filename.LastIndexOf(@"\") + 1), ImageFormat.Jpeg);

            if (firstImg)
            {
                firstImgSectors = sectorAverages;
                return;
            }
            SecondimgListSectors[secondImagePos] = sectorAverages;
        }

        /// <summary>
        /// This function get's the color from HSV values. This is only for data alalysis
        /// </summary>
        /// <param name="hue"></param>
        /// <param name="saturation"></param>
        /// <param name="value"></param>
        /// <returns></returns>
        public static Color ColorFromHSV(double hue, double saturation, double value)
        {
            int hi = Convert.ToInt32(Math.Floor(hue / 60)) % 6;
            double f = hue / 60 - Math.Floor(hue / 60);

            value = value * 255;
            int v = Convert.ToInt32(value);
            int p = Convert.ToInt32(value * (1 - saturation));
            int q = Convert.ToInt32(value * (1 - f * saturation));
            int t = Convert.ToInt32(value * (1 - (1 - f) * saturation));

            if (hi == 0)
                return Color.FromArgb(255, v, t, p);
            else if (hi == 1)
                return Color.FromArgb(255, q, v, p);
            else if (hi == 2)
                return Color.FromArgb(255, p, v, t);
            else if (hi == 3)
                return Color.FromArgb(255, p, q, v);
            else if (hi == 4)
                return Color.FromArgb(255, t, p, v);
            else
                return Color.FromArgb(255, v, p, q);
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

            List<int> xAxisHue = new List<int>();
            List<int> xAxisBrightness = new List<int>();
            List<int> xAxisSaturation = new List<int>();
            for (int b = 0; b <= diffHue.Max(); b++)
            {
                xAxisHue.Add(b);
            }

            if (xAxisHue.Count == 1) xAxisHue.Add(1);

            for (int d = 0; d <= diffBrightness.Max(); d++)
            {
                xAxisBrightness.Add(d);
            }

            if (xAxisBrightness.Count == 1) xAxisBrightness.Add(1);

            for (int d = 0; d <= diffSaturation.Max(); d++)
            {
                xAxisSaturation.Add(d);
            }

            if (xAxisSaturation.Count == 1) xAxisSaturation.Add(1);

            List<int> yAxisHue = new List<int>();
            List<int> yAxisBrightness = new List<int>();
            List<int> yAxisSaturation = new List<int>();
            for (int a = 0; a < xAxisHue.Count; a++)
            {
                yAxisHue.Add(diffHue.Where(x => x == xAxisHue[a]).ToList().Count);
            }

            for (int a = 0; a < xAxisBrightness.Count; a++)
            {
                yAxisBrightness.Add(diffBrightness.Where(x => x == xAxisBrightness[a]).ToList().Count);
            }

            for (int a = 0; a < xAxisSaturation.Count; a++)
            {
                yAxisSaturation.Add(diffSaturation.Where(x => x == xAxisSaturation[a]).ToList().Count);
            }


            ds.Tables[pos].TableName = secondImgSectorsCompare.FileName;
            ds.Tables[pos].Columns.Add("xAxisHue");
            ds.Tables[pos].Columns.Add("yAxisHue");
            ds.Tables[pos].Columns.Add("xAxisBrightness");
            ds.Tables[pos].Columns.Add("yAxisBrightness");
            ds.Tables[pos].Columns.Add("xAxisSaturation");
            ds.Tables[pos].Columns.Add("yAxisSaturation");

            var t = Task.Run(() => {
                for (int c = 0; c < xAxisHue.Count; c++)
                {
                    ds.Tables[pos].Rows.Add(xAxisHue[c], yAxisHue[c], xAxisBrightness.Count > c ? xAxisBrightness[c] : 0,
                        yAxisBrightness.Count > c ? yAxisBrightness[c] : 0,
                        xAxisSaturation.Count > c ? xAxisSaturation[c] : 0,
                        yAxisSaturation.Count > c ? yAxisSaturation[c] : 0);
                }
            });

            if (mode == Modes.Folder)
            {
                BeginInvoke(new MethodInvoker(delegate
                {
                    textBox11.Text = (diffHue.Average() / (diffHue.Max() / 100.0)).ToString() + "%";
                    comboBox1.Items.Add(secondImgSectorsCompare.FileName);
                }));
            }
            else
            {
                textBox11.Text = (diffHue.Average() / (diffHue.Max() / 100.0)).ToString() + "%";
                comboBox1.Items.Add(secondImgSectorsCompare.FileName);
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