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
    sealed partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
            System.Diagnostics.Process.GetCurrentProcess().PriorityClass = System.Diagnostics.ProcessPriorityClass.High;
        }

        private void button3_Click(object sender, EventArgs e)
        {
            ds = new DataSet();
            results = new List<(int, int, int, string, string)>();
            comboBox1.Items.Clear();
            comboBox1.SelectedIndex = -1;

            for (int a = 0; a < SecondimgListSectors.Length; a++)
            {
                ds.Tables.Add();
            }

            if (mode == Modes.Single)
            {
                results.Add(CompareImg(firstImgSectors, SecondimgListSectors[0], 0));
            }
            else
            {
                Thread[] threads = new Thread[25];
                (List<(int, int, int)>, string) firstimage = firstImgSectors;
                int length = SecondimgListSectors.Length / threads.Length;
                for (int a = 0; a < threads.Length; a++)
                {
                    int startPos = length * a;               
                    threads[a] = new Thread(() => ThreadRunCompare(startPos, length, firstimage));
                    threads[a].Start();
                }

                length = SecondimgListSectors.Length % threads.Length;
                int lastPos = SecondimgListSectors.Length - length;
                Thread lastThread = new Thread(() => ThreadRunCompare(lastPos, length, firstimage));
                lastThread.Start();

                foreach (var thread in threads)
                {
                    thread.Join();
                }

                lastThread.Join();
            }

            if (mode == Modes.Single)
            {
                textBox1.Text = results[0].Item1.ToString();
                textBox2.Text = results[0].Item2.ToString();
                textBox9.Text = results[0].Item3.ToString();
                textBox10.Text = ((results[0].Item1 + results[0].Item2 + results[0].Item3) / 3).ToString();
                comboBox1.Enabled = true;
                comboBox1.SelectedIndex = 0;
                return;
            }

            comboBox1.Sorted = true;
            comboBox1.Enabled = true;
            textBox14.Enabled = true;
        }

        private void button4_Click(object sender, EventArgs e)
        {
            throw new NotImplementedException();
        }

        private void exitToolStripMenuItem_Click(object sender, EventArgs e)
        {
            Close();
        }

        private void openAfbeelding1ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            openFileDialog1.ShowDialog();

            if (string.IsNullOrEmpty(openFileDialog1.SafeFileName) || openFileDialog1.SafeFileName.Contains("openFi")) return;

            Prepimage(openFileDialog1.FileName, true, 0);

            textBox13.Text = openFileDialog1.SafeFileName;
        }

        private void openAfbeelding2ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (mode == Modes.Folder) return;
            openFileDialog1.ShowDialog();

            if (string.IsNullOrEmpty(openFileDialog1.SafeFileName) || openFileDialog1.SafeFileName.Contains("openFi")) return;

            Prepimage(openFileDialog1.FileName, false, 0);

            button3.Enabled = true;
            button4.Enabled = true;
            textBox12.Text = openFileDialog1.SafeFileName;
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
            SecondimgListSectors = new (List<(int, int, int)>, string)[fileNames.Length];
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

            int pos2 = -1;

            for (int a = 0; a < ds.Tables.Count; a++)
            {
                if (ds.Tables[a].TableName == comboBox1.Items[comboBox1.SelectedIndex].ToString())
                {
                    pos2 = a;
                    break;
                }
            }

            chart1.DataSource = ds.Tables[pos2];
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
            List<string> fileNames = results.Select(r => r.Item5).ToList();
            int pos = fileNames.IndexOf(comboBox1.Items[comboBox1.SelectedIndex].ToString());

            textBox5.Text = (chart1.ChartAreas[0].AxisX.Minimum - 1).ToString();
            textBox6.Text = chart1.ChartAreas[0].AxisX.Maximum.ToString();
            textBox7.Text = chart1.ChartAreas[0].AxisY.Maximum.ToString();
            textBox8.Text = chart1.ChartAreas[0].AxisY.Minimum.ToString();

            textBox1.Text = results[pos].Item1.ToString();
            textBox2.Text = results[pos].Item2.ToString();
            textBox9.Text = results[pos].Item3.ToString();
            textBox10.Text = ((results[pos].Item1 + results[pos].Item2 + results[pos].Item3) / 3).ToString();
            textBox11.Text = results[pos].Item4;
            if (mode == Modes.Folder)
            {
                textBox12.Text = fileNames[pos];
            }
        }

        private void textBox14_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter && !string.IsNullOrEmpty(textBox7.Text) && Convert.ToInt32(textBox7.Text) > -1)
            {
                Directory.Delete(Environment.GetFolderPath(Environment.SpecialFolder.Desktop) + @"\resultaten\foto's", true);
                Directory.CreateDirectory(Environment.GetFolderPath(Environment.SpecialFolder.Desktop) + @"\resultaten\foto's");
                for (int a = 0; a < results.Count; a++)
                {
                    if (Convert.ToDouble(results[a].Item4.Remove(results[a].Item4.Length - 1, 1)) <= Convert.ToDouble(textBox14.Text))
                    {
                        File.Copy(fileNames[a], Environment.GetFolderPath(Environment.SpecialFolder.Desktop) + @"\resultaten\foto's\" + 
                            fileNames[a].Substring(fileNames[comboBox1.SelectedIndex].LastIndexOf(@"\") + 1) + " " + results[a].Item4.Remove(results[a].Item4.Length - 1, 1) + ".jpg");
                    }
                }
            }
        }
    }
}
