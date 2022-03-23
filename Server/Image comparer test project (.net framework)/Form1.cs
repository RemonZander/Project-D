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

namespace Image_comparer_test_project__.net_framework_
{
    public partial class Form1 : Form
    {
        private Bitmap firstImg, secondimage;
        private (int, int, int)[,] firstImgSectorsHue = new (int, int, int)[WidthSectors, HeightSectors];
        private (int, int, int)[][,] SecondimgListSectorsHue = new (int, int, int)[1][,];
        private DataSet ds = new DataSet();
        private List<(int, int, int, string)> results;
        private string[] fileNames = new string[1];

        //only square supported for now
        private const int WidthSectors = 41;
        private const int HeightSectors = 41;

        private readonly Bitmap image = new Bitmap(600, 450);       

        private PixelWeights PixelWeights = PixelWeights.Geen;

        private Modes mode = Modes.Single;

        public Form1()
        {
            InitializeComponent();       
        }

        private void button3_Click(object sender, EventArgs e)
        {
            ds = new DataSet();
            results = new List<(int, int, int, string)>();
            comboBox1.Items.Clear();
            comboBox1.SelectedIndex = -1;

            if (mode == Modes.Single)
            {
                results.Add(CompareImg(firstImgSectorsHue, SecondimgListSectorsHue[0], 0));
            }
            else
            {
                for (int a = 0; a < SecondimgListSectorsHue.Length; a++)
                {
                    results.Add(CompareImg(firstImgSectorsHue, SecondimgListSectorsHue[a], a));
                }
            }
           
            if (mode == Modes.Single)
            {
                textBox1.Text = results[0].Item1.ToString();
                textBox2.Text = results[0].Item2.ToString();
                textBox9.Text = results[0].Item3.ToString();
                textBox10.Text = ((results[0].Item1 + results[0].Item2 + results[0].Item3) / 3).ToString();
            }

            comboBox1.Enabled = true;
            textBox14.Enabled = true;
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

        private void Prepimage(Bitmap image, bool firstImg, int count)
        {
            (int, int, int)[,] sectorAverages = new (int, int, int)[WidthSectors, HeightSectors];
            int sectorWidth = image.Width / WidthSectors;
            int sectorheight = image.Height / HeightSectors;
            int totalPixelsPerSector = sectorWidth * sectorheight;

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

                    for (int c = 0; c < sectorWidth; c++)
                    {
                        for (int d = 0; d < sectorheight; d++)
                        {
                            Color pixelColor = image.GetPixel(a * sectorWidth + c, b * sectorheight + d);

                            TotalHueValues += (int)pixelColor.GetHue();
                            totalBrightnessValues += (int)(pixelColor.GetBrightness() * 100);
                            totalSaturationValues += (int)(pixelColor.GetSaturation() * 100);
                        }
                    }

                    sectorAverages[a, b] = ((int)(TotalHueValues / totalPixelsPerSector * weight), (int)(totalBrightnessValues / totalPixelsPerSector * weight), (int)(totalSaturationValues / totalPixelsPerSector * weight));
                }
            }          

            if (firstImg)
            {
                firstImgSectorsHue = sectorAverages;
                return;
            }
            SecondimgListSectorsHue[count] = sectorAverages;
        }

        private void button4_Click(object sender, EventArgs e)
        {
            throw new NotImplementedException();

            ds = new DataSet();
            comboBox1.Items.Clear();
            comboBox1.SelectedIndex = -1;
            Prepimage(firstImg, false, 0);
            Prepimage(secondimage, false, 0);
            results.Add(CompareImg(firstImgSectorsHue, SecondimgListSectorsHue[0], 0));

            textBox1.Text = results[0].Item1.ToString();
            textBox2.Text = results[0].Item2.ToString();
            textBox9.Text = results[0].Item3.ToString();

            comboBox1.Enabled = true;
        }

        private void exitToolStripMenuItem_Click(object sender, EventArgs e)
        {
            Close();
        }

        private void openAfbeelding1ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            openFileDialog1.ShowDialog();

            if (string.IsNullOrEmpty(openFileDialog1.SafeFileName) || openFileDialog1.SafeFileName.Contains("openFi")) return;

            textBox13.Text = openFileDialog1.SafeFileName;

            firstImg = (Bitmap)Bitmap.FromFile(openFileDialog1.FileName);

            double ratio = firstImg.Height * 1.0 / firstImg.Width;
            firstImg = CropAtRect(firstImg, new Rectangle(0, 0, 600, (int)(600 * ratio)));

            Prepimage(firstImg, true, 0);
        }

        private void openAfbeelding2ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (mode == Modes.Folder) return;
            openFileDialog1.ShowDialog();

            if (string.IsNullOrEmpty(openFileDialog1.SafeFileName) || openFileDialog1.SafeFileName.Contains("openFi")) return;

            button3.Enabled = true;
            button4.Enabled = true;
            textBox12.Text = openFileDialog1.SafeFileName;

            secondimage = (Bitmap)Bitmap.FromFile(openFileDialog1.FileName);

            double ratio = secondimage.Height * 1.0 / secondimage.Width;
            secondimage = CropAtRect(secondimage, new Rectangle(0, 0, 600, (int)(600 * ratio)));

            Prepimage(secondimage, false, 0);
        }

        private void geenToolStripMenuItem_Click(object sender, EventArgs e)
        {
            PixelWeights = PixelWeights.Geen;
            textBox4.Text = PixelWeights.Geen.ToString();
        }

        private void logaritmischToolStripMenuItem_Click(object sender, EventArgs e)
        {
            PixelWeights = PixelWeights.Logaritmisch;
            textBox4.Text = PixelWeights.Logaritmisch.ToString();
        }

        private void linearToolStripMenuItem_Click(object sender, EventArgs e)
        {
            PixelWeights = PixelWeights.Linear;
            textBox4.Text = PixelWeights.Linear.ToString();
        }

        private void vierakantToolStripMenuItem_Click(object sender, EventArgs e)
        {
            PixelWeights = PixelWeights.Vierkant;
            textBox4.Text = PixelWeights.Vierkant.ToString();
        }

        private void exponentieelToolStripMenuItem_Click(object sender, EventArgs e)
        {
            PixelWeights = PixelWeights.Exponentieel;
            textBox4.Text = PixelWeights.Exponentieel.ToString();
        }

        private void openFolderToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (mode == Modes.Single) return;

            folderBrowserDialog1.ShowDialog();

            if (string.IsNullOrEmpty(folderBrowserDialog1.SelectedPath)) return;
            
            string folder = folderBrowserDialog1.SelectedPath;

            fileNames = Directory.GetFiles(folder);
            SecondimgListSectorsHue = new (int, int, int)[fileNames.Length][,];

            List<Thread> threads = new List<Thread>();
            for (int b = 0; b < 20; b++)
            {
                threads.Add(new Thread(() => Prepimage(secondimage, false, 0)));
            }

            for (int a = 0; a < fileNames.Length; a++)
            {
                List<Thread> inactive = threads.Where(t => t.ThreadState != ThreadState.Running).ToList();

                Bitmap image = (Bitmap)Bitmap.FromFile(fileNames[a]);

                double ratio = image.Height * 1.0 / image.Width;
                image = CropAtRect(image, new Rectangle(0, 0, 600, (int)(600 * ratio)));

                int b = a;
                inactive[0] = new Thread(() => Prepimage(image, false, b));
                inactive[0].Start();
            }

            foreach (var thread in threads)
            {
                if (thread.ThreadState == ThreadState.Running)
                {
                    thread.Join();
                }
            }

            button3.Enabled = true;
            button4.Enabled = true;
        }

        private void singleModeToolStripMenuItem_Click(object sender, EventArgs e)
        {
            mode = Modes.Single;
            textBox3.Text = Modes.Single.ToString();
        }

        private void folderModeToolStripMenuItem_Click(object sender, EventArgs e)
        {
            mode = Modes.Folder;
            textBox3.Text = Modes.Folder.ToString();
        }

        private void textBox5_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter && !string.IsNullOrEmpty(textBox5.Text) && Convert.ToInt32(textBox5.Text) > -1)
            {
                chart1.ChartAreas[0].AxisX.Minimum = Convert.ToDouble(textBox5.Text) + 1;
            }
        }

        private void textBox6_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter && !string.IsNullOrEmpty(textBox6.Text) && Convert.ToInt32(textBox6.Text) > -1)
            {
                chart1.ChartAreas[0].AxisX.Maximum = Convert.ToDouble(textBox6.Text) + 1;
            }
        }

        private void textBox8_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter && !string.IsNullOrEmpty(textBox8.Text) && Convert.ToInt32(textBox8.Text) > -1)
            {
                chart1.ChartAreas[0].AxisY.Minimum = Convert.ToDouble(textBox8.Text);
            }
        }

        private void textBox7_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter && !string.IsNullOrEmpty(textBox7.Text) && Convert.ToInt32(textBox7.Text) > -1)
            {
                chart1.ChartAreas[0].AxisY.Maximum = Convert.ToDouble(textBox7.Text);
            }
        }

        private void comboBox1_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (comboBox1.SelectedIndex == -1) return;

            chart1.DataSource = ds.Tables[comboBox1.SelectedIndex];
            chart1.Series[0].ChartType = System.Windows.Forms.DataVisualization.Charting.SeriesChartType.Line;
            chart1.Series[0].XValueType = System.Windows.Forms.DataVisualization.Charting.ChartValueType.Int32;
            chart1.Series[0].YValueType = System.Windows.Forms.DataVisualization.Charting.ChartValueType.Int32;
            chart1.Series[0].LegendText = "match results Hue";
            chart1.Series[0].XValueMember = "xAxisHue";
            chart1.Series[0].YValueMembers = "yAxisHue";
            chart1.Series[0].IsVisibleInLegend = true;

            chart1.Series[1].ChartType = System.Windows.Forms.DataVisualization.Charting.SeriesChartType.Line;
            chart1.Series[1].XValueType = System.Windows.Forms.DataVisualization.Charting.ChartValueType.Int32;
            chart1.Series[1].YValueType = System.Windows.Forms.DataVisualization.Charting.ChartValueType.Int32;
            chart1.Series[1].LegendText = "match results Brightness";
            chart1.Series[1].XValueMember = "xAxisBrightness";
            chart1.Series[1].YValueMembers = "yAxisBrightness";
            chart1.Series[1].IsVisibleInLegend = true;

            chart1.Series[2].ChartType = System.Windows.Forms.DataVisualization.Charting.SeriesChartType.Line;
            chart1.Series[2].XValueType = System.Windows.Forms.DataVisualization.Charting.ChartValueType.Int32;
            chart1.Series[2].YValueType = System.Windows.Forms.DataVisualization.Charting.ChartValueType.Int32;
            chart1.Series[2].LegendText = "match results Saturation";
            chart1.Series[2].XValueMember = "xAxisSaturation";
            chart1.Series[2].YValueMembers = "yAxisSaturation";
            chart1.Series[2].IsVisibleInLegend = true;
            chart1.DataBind();

            chart1.Update();

            textBox5.Text = (chart1.ChartAreas[0].AxisX.Minimum - 1).ToString();
            textBox6.Text = chart1.ChartAreas[0].AxisX.Maximum.ToString();
            textBox7.Text = chart1.ChartAreas[0].AxisY.Maximum.ToString();
            textBox8.Text = chart1.ChartAreas[0].AxisY.Minimum.ToString();

            textBox1.Text = results[comboBox1.SelectedIndex].Item1.ToString();
            textBox2.Text = results[comboBox1.SelectedIndex].Item2.ToString();
            textBox9.Text = results[comboBox1.SelectedIndex].Item3.ToString();
            textBox10.Text = ((results[comboBox1.SelectedIndex].Item1 + results[comboBox1.SelectedIndex].Item2 + results[comboBox1.SelectedIndex].Item3) / 3).ToString();
            textBox11.Text = results[comboBox1.SelectedIndex].Item4;
            textBox12.Text = fileNames[comboBox1.SelectedIndex].Substring(fileNames[comboBox1.SelectedIndex].LastIndexOf(@"\") + 1);
        }

        private void textBox14_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter && !string.IsNullOrEmpty(textBox7.Text) && Convert.ToInt32(textBox7.Text) > -1)
            {
                Directory.Delete(Environment.GetFolderPath(Environment.SpecialFolder.Desktop) + @"\resultaten\foto's", true);
                Directory.CreateDirectory(Environment.GetFolderPath(Environment.SpecialFolder.Desktop) + @"\resultaten\foto's");
                for (int a = 0; a < results.Count; a++)
                {
                    double test = Convert.ToDouble(results[a].Item4.Remove(results[a].Item4.Length - 1, 1));
                    if (Convert.ToDouble(results[a].Item4.Remove(results[a].Item4.Length - 1, 1)) <= Convert.ToDouble(textBox14.Text))
                    {
                        File.Copy(fileNames[a], Environment.GetFolderPath(Environment.SpecialFolder.Desktop) + @"\resultaten\foto's\" + 
                            fileNames[a].Substring(fileNames[comboBox1.SelectedIndex].LastIndexOf(@"\") + 1) + " " + results[a].Item4.Remove(results[a].Item4.Length - 1, 1) + ".jpg");
                    }
                }
            }
        }

        private (int, int, int, string) CompareImg((int, int, int)[,] firstImgSectorsCompare, (int, int, int)[,] secondImgSectorsCompare, int iteration)
        {
            List<int> diffHue = new List<int>();
            List<int> diffBrightness = new List<int>();
            List<int> diffSaturation = new List<int>();
            List<(int, int, int)> firstImgSectorsCompareList = new List<(int, int, int)>();
            List<(int, int, int)> secondImgSectorsCompareList = new List<(int, int, int)>();

            for (int b = 0; b < firstImgSectorsCompare.Length; b++)
            {
                firstImgSectorsCompareList.Add((firstImgSectorsCompare[b % WidthSectors, b / HeightSectors].Item1, firstImgSectorsCompare[b % WidthSectors, b / HeightSectors].Item2, firstImgSectorsCompare[b % WidthSectors, b / HeightSectors].Item3));
                secondImgSectorsCompareList.Add((secondImgSectorsCompare[b % WidthSectors, b / HeightSectors].Item1, secondImgSectorsCompare[b % WidthSectors, b / HeightSectors].Item2, secondImgSectorsCompare[b % WidthSectors, b / HeightSectors].Item3));
            }

            firstImgSectorsCompareList = firstImgSectorsCompareList.OrderBy(x => x.Item1).ToList();
            secondImgSectorsCompareList = secondImgSectorsCompareList.OrderBy(x => x.Item1).ToList();

            for (int a = 0; a < firstImgSectorsCompareList.Count; a++)
            {
                diffHue.Add(ToUInt16(firstImgSectorsCompareList[a].Item1 - secondImgSectorsCompareList[a].Item1));
            }

            firstImgSectorsCompareList = firstImgSectorsCompareList.OrderBy(x => x.Item2).ToList();
            secondImgSectorsCompareList = secondImgSectorsCompareList.OrderBy(x => x.Item2).ToList();

            for (int a = 0; a < firstImgSectorsCompareList.Count; a++)
            {
                diffBrightness.Add(ToUInt16(firstImgSectorsCompareList[a].Item2 - secondImgSectorsCompareList[a].Item2));
            }

            firstImgSectorsCompareList = firstImgSectorsCompareList.OrderBy(x => x.Item3).ToList();
            secondImgSectorsCompareList = secondImgSectorsCompareList.OrderBy(x => x.Item3).ToList();

            for (int a = 0; a < firstImgSectorsCompareList.Count; a++)
            {
                diffSaturation.Add(ToUInt16(firstImgSectorsCompareList[a].Item3 - secondImgSectorsCompareList[a].Item3));
            }

            List<int> xAxisHue = new List<int>();
            List<int> xAxisBrightness = new List<int>();
            List<int> xAxisSaturation = new List<int>();
            for (int b = 0; b <= diffHue.Max(); b++)
            {
                xAxisHue.Add(b);
            }

            for (int d = 0; d <= diffBrightness.Max(); d++)
            {
                xAxisBrightness.Add(d);
            }

            for (int d = 0; d <= diffSaturation.Max(); d++)
            {
                xAxisSaturation.Add(d);
            }

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
           
            ds.Tables.Add();
            ds.Tables[ds.Tables.Count - 1].Columns.Add("xAxisHue");
            ds.Tables[ds.Tables.Count - 1].Columns.Add("yAxisHue");
            ds.Tables[ds.Tables.Count - 1].Columns.Add("xAxisBrightness");
            ds.Tables[ds.Tables.Count - 1].Columns.Add("yAxisBrightness");
            ds.Tables[ds.Tables.Count - 1].Columns.Add("xAxisSaturation");
            ds.Tables[ds.Tables.Count - 1].Columns.Add("yAxisSaturation");

            for (int c = 0; c < xAxisHue.Count; c++)
            {
                ds.Tables[ds.Tables.Count - 1].Rows.Add(xAxisHue[c], yAxisHue[c], xAxisBrightness.Count > c ? xAxisBrightness[c] : 0,
                    yAxisBrightness.Count > c ? yAxisBrightness[c] : 0,
                    xAxisSaturation.Count > c ? xAxisSaturation[c] : 0,
                    yAxisSaturation.Count > c ? yAxisSaturation[c] : 0);
            }

            textBox11.Text = (diffHue.Average() / (diffHue.Max() / 100.0)).ToString() + "%";
            comboBox1.Items.Add(ds.Tables.Count - 1);

            return ((int)diffHue.Average(), (int)diffBrightness.Average(), (int)diffSaturation.Average(), (diffHue.Average() / (diffHue.Max() / 100.0)).ToString() + "%");
        }

    }
}
