using System.Drawing;
using System.Collections.Generic;
using System.Threading;
namespace Image_comparer_test_project
{
    public partial class Form1 : Form
    {
        private Bitmap firstImg, secondimage;
        private Tuple<int, int, int>[,] firstImgSectors = new Tuple<int, int, int>[WidthSectors, HeightSectors];
        private Tuple<int, int, int>[][,] SecondimgListSectors = new Tuple<int, int, int>[1][,];

        private const int WidthSectors = 20;
        private const int HeightSectors = 20;
  
        private Bitmap image = new Bitmap(600, 450);
        private Graphics g;
        public Form1()
        {
            InitializeComponent();
            g = Graphics.FromImage(image);
        }

        private void button2_Click(object sender, EventArgs e)
        {
            openFileDialog1.ShowDialog();

            if (string.IsNullOrEmpty(openFileDialog1.SafeFileName) || openFileDialog1.SafeFileName.Contains("openFi")) return;
            SecondimgListSectors = new Tuple<int, int, int>[1][,];

            secondimage = (Bitmap)Bitmap.FromFile(openFileDialog1.FileName);
            secondimage = CropAtRect(secondimage, new Rectangle(0, 0, secondimage.Width - (secondimage.Width - 800), (int)(800 * (1.0 * secondimage.Height / secondimage.Width))));

            Thread makeSectors = new Thread(() => Prepimage(secondimage, false));
            makeSectors.Start();
        }

        private void button3_Click(object sender, EventArgs e)
        {
            
            for (int a = 0; a < WidthSectors; a++)
            {
                Pen p = new Pen(Color.Black);
                g.DrawLine(p, new Point(a * (600 / WidthSectors), 0), new Point(a * (600 / WidthSectors), 450));
            }

            for (int b = 0; b < HeightSectors; b++)
            {
                Pen p = new Pen(Color.Black);
                g.DrawLine(p, new Point(0, b * (450 / HeightSectors)), new Point(600, b * (450 / HeightSectors)));
            }
            
            pictureBox1.Image = image;
            pictureBox1.Update();

            int simularity = CompareImg(firstImgSectors, SecondimgListSectors[0]);
            //textBox1.Text = ToUInt16(100 / 75 * (75 - simularity)).ToString();
            textBox1.Text = simularity.ToString();

            pictureBox1.Image = image;
            pictureBox1.Update();
        }

        private int CompareImg(Tuple<int, int, int>[,] firstImgSectorsCompare, Tuple<int, int, int>[,] secondImgSectorsCompare)
        {
            List<int> matched = new List<int>();
            int count = 0;
            (List<int>, int) bestMatch = (new List<int>(), 99999999);
            foreach (var sector in firstImgSectorsCompare)
            {
                count++;
                bestMatch.Item2 = 99999999;
                bestMatch.Item1.Add(-1);
                for (int a = 0; a < secondImgSectorsCompare.Length; a++)
                {
                    int difference = ToUInt16(sector.Item1 - secondImgSectorsCompare[a % WidthSectors, a / HeightSectors].Item1) +
                        ToUInt16(sector.Item2 - secondImgSectorsCompare[a % WidthSectors, a / HeightSectors].Item2) +
                        ToUInt16(sector.Item3 - secondImgSectorsCompare[a % WidthSectors, a / HeightSectors].Item3);

                    if (difference < bestMatch.Item2 && !bestMatch.Item1.Contains(a))
                    {
                        bestMatch.Item1[^1] = a;
                        bestMatch.Item2 = difference;
                    }
                }

                //g.DrawImage(secondimage, new Rectangle(0, 0, 100, 100));
                //g.DrawImage(secondimage, new Rectangle(bestMatch.Item1[^1] % WidthSectors * (600 / WidthSectors), bestMatch.Item1[^1] / HeightSectors * (450 / HeightSectors), 600 / WidthSectors, 450 / HeightSectors), 
                //    new Rectangle(count % WidthSectors * (600 / WidthSectors), count / HeightSectors * (450 / HeightSectors), 600 / WidthSectors, 450 / HeightSectors), GraphicsUnit.Pixel);
                g.DrawImage(secondimage, new Rectangle(bestMatch.Item1[^1] % WidthSectors * (600 / WidthSectors), bestMatch.Item1[^1] / HeightSectors * (450 / HeightSectors), 600 / WidthSectors, 450 / HeightSectors), 
                    new Rectangle(count % WidthSectors * (600 / WidthSectors), count / HeightSectors * (450 / HeightSectors), 600 / WidthSectors, 450 / HeightSectors), GraphicsUnit.Pixel);
                matched.Add(bestMatch.Item2);
            }

            return (int)matched.Average();
        }

        private static int ToUInt16(int number)
        {
            if (number < 0) return -number;
            return number;
        }

        private void Prepimage(Bitmap image, bool firstImg)
        {
            Tuple<int, int, int>[,] sectorAverages = new Tuple<int, int, int>[WidthSectors, HeightSectors];
            int sectorWidth = image.Width / WidthSectors;
            int sectorheight = image.Height / HeightSectors;
            int totalPixelsPerSector = sectorWidth * sectorheight;


            for (int a = 0; a < WidthSectors; a++)
            {
                for (int b = 0; b < HeightSectors; b++)
                {
                    (int, int, int) TotalColorValues = (0, 0, 0);
                    for (int c = 0; c < sectorWidth; c++)
                    {
                        for (int d = 0; d < sectorheight; d++)
                        {                           
                            Color pixelColor = image.GetPixel(a * sectorWidth + c, b * sectorheight + d);
                            TotalColorValues.Item1 += pixelColor.R;
                            TotalColorValues.Item2 += pixelColor.G;
                            TotalColorValues.Item3 += pixelColor.B;
                        }
                    }

                    sectorAverages[a, b] = new Tuple<int, int, int>(TotalColorValues.Item1 / totalPixelsPerSector,
                        TotalColorValues.Item2 / totalPixelsPerSector,
                        TotalColorValues.Item3 / totalPixelsPerSector);
                }
            }

            if (firstImg)
            {
                firstImgSectors = sectorAverages;
                return;
            }
            SecondimgListSectors[0] = sectorAverages;
        }

        private void button1_Click(object sender, EventArgs e)
        {
            openFileDialog1.ShowDialog();

            if (string.IsNullOrEmpty(openFileDialog1.SafeFileName) || openFileDialog1.SafeFileName.Contains("openFi")) return;

            firstImg = (Bitmap)Bitmap.FromFile(openFileDialog1.FileName);

            firstImg = CropAtRect(firstImg, new Rectangle(0, 0, firstImg.Width - (firstImg.Width - 800), (int)(800 * (1.0 * firstImg.Height / firstImg.Width))));

            Thread makeSectors = new Thread(() => Prepimage(firstImg, true));
            makeSectors.Start();
        }

        private static Bitmap CropAtRect(Bitmap b, Rectangle r)
        {
            Bitmap nb = new Bitmap(r.Width, r.Height);
            using Graphics g = Graphics.FromImage(nb);
            g.DrawImage(b, -r.X, -r.Y);
            return nb;
        }
    }
}