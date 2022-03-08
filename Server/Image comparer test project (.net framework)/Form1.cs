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

namespace Image_comparer_test_project__.net_framework_
{
    public partial class Form1 : Form
    {
        private Bitmap firstImg, secondimage;
        private (int, int)[,] firstImgSectorsHue = new (int, int)[WidthSectors, HeightSectors];
        private (int, int)[][,] SecondimgListSectorsHue = new (int, int)[1][,];

        //only square supported for now
        private const int WidthSectors = 41;
        private const int HeightSectors = 41;

        private readonly Bitmap image = new Bitmap(600, 450);
        private readonly Graphics g;

        public Form1()
        {
            InitializeComponent();

            g = Graphics.FromImage(image);
            comboBox1.SelectedIndex = 1;
        }

        private void button1_Click(object sender, EventArgs e)
        {
            openFileDialog1.ShowDialog();

            if (string.IsNullOrEmpty(openFileDialog1.SafeFileName) || openFileDialog1.SafeFileName.Contains("openFi")) return;

            button2.Enabled = true;

            firstImg = (Bitmap)Bitmap.FromFile(openFileDialog1.FileName);

            double ratio = firstImg.Height * 1.0 / firstImg.Width;
            firstImg = CropAtRect(firstImg, new Rectangle(0, 0, 600, (int)(600 * ratio)));

            
            //Thread makeSectors = new Thread(() => Prepimage(firstImg, true));
            // makeSectors = new Thread(() => Prepimage(firstImg, true));
            Prepimage(firstImg, true);
            //makeSectors.Start();
        }

        private void button2_Click(object sender, EventArgs e)
        {
            openFileDialog1.ShowDialog();

            if (string.IsNullOrEmpty(openFileDialog1.SafeFileName) || openFileDialog1.SafeFileName.Contains("openFi")) return;

            button3.Enabled = true;
            button4.Enabled = true;

            secondimage = (Bitmap)Bitmap.FromFile(openFileDialog1.FileName);

            double ratio = secondimage.Height * 1.0 / secondimage.Width;
            secondimage = CropAtRect(secondimage, new Rectangle(0, 0, 600, (int)(600 * ratio)));

            //Thread makeSectors = new Thread(() => Prepimage(firstImg, false));
            //Thread makeSectors = new Thread(() => Prepimage(secondimage, false));
            Prepimage(secondimage, false);
            //makeSectors.Start();
        }

        private void button3_Click(object sender, EventArgs e)
        {
            Result result = new Result();
            //result.Show();
            (int, int) results = CompareImg(firstImgSectorsHue, SecondimgListSectorsHue[0]);

            g.DrawImage(secondimage, new Point(0, 0));
            result.Image = image;

            for (int a = 0; a < WidthSectors; a++)
            {
                Pen p = new Pen(Color.Black);
                g.DrawLine(p, new Point(a * (firstImg.Width / WidthSectors), 0), new Point(a * (firstImg.Width / WidthSectors), firstImg.Height));
            }

            for (int b = 0; b < HeightSectors; b++)
            {
                Pen p = new Pen(Color.Black);
                g.DrawLine(p, new Point(0, b * (firstImg.Height / HeightSectors)), new Point(firstImg.Width, b * (firstImg.Height / HeightSectors)));
            }

            
            result.Image = image;
            textBox1.Text = results.Item1.ToString();
            textBox2.Text = results.Item2.ToString();

        }

        private static Bitmap CropAtRect(Bitmap b, Rectangle r)
        {
            Bitmap nb = new Bitmap(r.Width, r.Height);
            Graphics g = Graphics.FromImage(nb);
            g.DrawImage(b, -r.X, -r.Y, nb.Width, nb.Height);
            return nb;
        }

        private static UInt16 ToUInt16(int number)
        {
            if (number < 0) return (UInt16)(-number);
            return (UInt16)number;
        }

        private void Prepimage(Bitmap image, bool firstImg)
        {
            Bitmap nb = new Bitmap(image.Width, image.Height);
            Graphics g = Graphics.FromImage(nb);
            (int, int)[,] sectorAverages = new (int, int)[WidthSectors, HeightSectors];
            int sectorWidth = image.Width / WidthSectors;
            int sectorheight = image.Height / HeightSectors;
            int totalPixelsPerSector = sectorWidth * sectorheight;


            for (int a = 0; a < WidthSectors; a++)
            {
                for (int b = 0; b < HeightSectors; b++)
                {
                    int TotalHueValues = 0;
                    int totalBrightnessValues = 0;
                    var red = 0;
                    var green = 0;
                    var blue = 0;
                    var alpha = 0;

                    double weight = 1;
                    if (comboBox1.SelectedIndex == 0)
                    {
                        if (a < b)
                        {
                            if (a == 0)
                            {
                                weight = 1;
                            }
                            else
                            {
                                weight = Math.Log(a) * a + 1.0;
                            }

                        }
                        else
                        {
                            if (b == 0)
                            {
                                weight = 1;
                            }
                            else
                            {
                                weight = Math.Log(b) * a + 1.0;
                            }
                        }
                    }
                    else if (comboBox1.SelectedIndex == 1 || comboBox1.SelectedIndex == -1)
                    {
                        if ((WidthSectors / 2 - ToUInt16(WidthSectors / 2 - a)) < (WidthSectors / 2 - ToUInt16(WidthSectors / 2 - b)))
                        {
                            weight = 0.08 * (WidthSectors / 2 - ToUInt16(WidthSectors / 2 - a)) + 1;

                        }
                        else
                        {
                            weight = 0.08 * (WidthSectors / 2 - ToUInt16(WidthSectors / 2 - b)) + 1;
                        }
                    }
                    else if (comboBox1.SelectedIndex == 2)
                    {
                        if (a < b)
                        {
                            weight = 2.0 * a + 1;

                        }
                        else
                        {
                            weight = 2.0 * b + 1;
                        }
                    }
                    else if (comboBox1.SelectedIndex == 3)
                    {
                        if (a < b)
                        {
                            weight = a * a + 1.0;

                        }
                        else
                        {
                            weight = b * b + 1.0;
                        }
                    }

                    for (int c = 0; c < sectorWidth; c++)
                    {
                        for (int d = 0; d < sectorheight; d++)
                        {
                            Color pixelColor = image.GetPixel(a * sectorWidth + c, b * sectorheight + d);
                            var saturation = pixelColor.GetSaturation() * 100.0;
                            var brightness = pixelColor.GetBrightness() * 100.0;
                            var hue = pixelColor.GetHue();

                            //TotalColorValues += (int)(pixelColor.GetHue() + (pixelColor.GetSaturation() * 100.0) + (pixelColor.GetBrightness() * 100.0));
                            TotalHueValues += (int)pixelColor.GetHue();
                            totalBrightnessValues += (int)(pixelColor.GetBrightness() * 100);
                            red += pixelColor.R;
                            green += pixelColor.G;
                            blue += pixelColor.B;
                            alpha += pixelColor.A;
                        }
                    }
                    alpha = alpha / totalPixelsPerSector;
                    red = red / totalPixelsPerSector;
                    green = green / totalPixelsPerSector;
                    blue = blue / totalPixelsPerSector;
                    g.FillRectangle(new SolidBrush(Color.FromArgb(alpha, red, green, blue)), 
                        new Rectangle(sectorWidth * a, sectorheight * b, sectorWidth, sectorheight));

                    g.DrawString((totalBrightnessValues / totalPixelsPerSector * weight).ToString(), new Font("Arial", 6), new SolidBrush(Color.Black), sectorWidth * a, sectorheight * b);

                    sectorAverages[a, b] = ((int)(TotalHueValues / totalPixelsPerSector * weight), (int)(totalBrightnessValues / totalPixelsPerSector * weight));
                }
            }

           

            if (firstImg)
            {
                firstImgSectorsHue = sectorAverages;
                nb.Save(@"C:\Users\remon\Desktop\resultaten\values 1.jpeg");
                return;
            }
            SecondimgListSectorsHue[0] = sectorAverages;
            nb.Save(@"C:\Users\remon\Desktop\resultaten\values 2.jpeg");
        }

        private void button4_Click(object sender, EventArgs e)
        {
            Prepimage(firstImg, false);
            Prepimage(secondimage, false);
            (int, int) results = CompareImg(firstImgSectorsHue, SecondimgListSectorsHue[0]);

            textBox1.Text = results.Item1.ToString();
            textBox1.Text = results.Item2.ToString();
        }

        private (int, int) CompareImg((int, int)[,] firstImgSectorsCompare, (int, int)[,] secondImgSectorsCompare)
        {
            List<int> diffHue = new List<int>();
            List<int> diffBrightness = new List<int>();
            for (int a = 0; a < firstImgSectorsCompare.Length; a++)
            {
                diffHue.Add(ToUInt16(firstImgSectorsCompare[a % WidthSectors, a / HeightSectors].Item1 - secondImgSectorsCompare[a % WidthSectors, a / HeightSectors].Item1));
                diffBrightness.Add(ToUInt16(firstImgSectorsCompare[a % WidthSectors, a / HeightSectors].Item2 - secondImgSectorsCompare[a % WidthSectors, a / HeightSectors].Item2));
            }

            List<int> xAxis = new List<int>();
            for (int b = 0; b <= diffHue.Max() / 2; b++)
            {
                if (b * 2 > 200) break;
                xAxis.Add(b * 2);
            }

            List<int> yAxis = new List<int>();
            for (int a = 0; a < xAxis.Count; a++)
            {
                if (a == xAxis.Count - 1)
                {
                    yAxis.Add(diffHue.Where(x => x >= xAxis[a] && x < xAxis[a] + 2).ToList().Count);
                    break;
                }
                yAxis.Add(diffHue.Where(x => x >= xAxis[a] && x < xAxis[a + 1]).ToList().Count);
            }

            DataSet ds = new DataSet();
            ds.Tables.Add();
            ds.Tables[0].Columns.Add("xAxis");
            ds.Tables[0].Columns.Add("yAxis");
            ds.Tables[0].Rows.Add(image);

            for (int c = 0; c < xAxis.Count; c++)
            {
                ds.Tables[0].Rows.Add(xAxis[c], yAxis[c]);
            }

            chart1.DataSource = ds;
            chart1.Series[0].ChartType = System.Windows.Forms.DataVisualization.Charting.SeriesChartType.Line;
            chart1.Series[0].XValueType = System.Windows.Forms.DataVisualization.Charting.ChartValueType.Int32;
            chart1.Series[0].YValueType = System.Windows.Forms.DataVisualization.Charting.ChartValueType.Int32;
            chart1.Series[0].LegendText = "match results";
            chart1.Series[0].XValueMember = "xAxis";
            chart1.Series[0].YValueMembers = "yAxis";
            chart1.Series[0].IsVisibleInLegend = true;
            chart1.DataBind();

            return ((int)diffHue.Average(), (int)diffBrightness.Average());
        }

    }
}
