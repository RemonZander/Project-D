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

        //only square supported for now
        private const int WidthSectors = 31;
        private const int HeightSectors = 31;
  
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

            double ratio = secondimage.Height * 1.0 / secondimage.Width;
            secondimage = CropAtRect(secondimage, new Rectangle(0, 0, 600, (int)(600 * ratio)));

            Thread makeSectors = new Thread(() => Prepimage(secondimage, false));
            makeSectors.Start();
        }

        private void button3_Click(object sender, EventArgs e)
        {
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
            
            pictureBox1.Image = image;
            pictureBox1.Update();

            //int simularity = CompareImg(firstImgSectors, SecondimgListSectors[0]);

            int simularity = CompareImg(firstImgSectors, SecondimgListSectors[0]);
            
            //textBox1.Text = ToUInt16(100 / 75 * (75 - simularity)).ToString();
            textBox1.Text = simularity.ToString();

            pictureBox1.Image = image;
            pictureBox1.Update();
        }

        private int CompareImg(Tuple<int, int, int>[,] firstImgSectorsCompare, Tuple<int, int, int>[,] secondImgSectorsCompare)
        {
            //double heightSectorMultiplication = 1 / HeightSectors;
            int[] firstNumerList = Enumerable.Range(0, firstImgSectorsCompare.Length).ToArray();
            int[] secondNumerList = Enumerable.Range(0, secondImgSectorsCompare.Length).ToArray();
            List<int> matched = new List<int>();

            int bestMatch = 99999999;
            for (int b = 0; b < firstImgSectorsCompare.Length; b++)
            {
                if (firstNumerList[b] == -1) continue;
                bestMatch = 99999999;

                int firstImgSector = 0;
                int secondImgSector = 0;
                for (int c = 0; c < firstImgSectorsCompare.Length; c++)
                {
                    if (firstNumerList[c] == -1) continue;
                    Tuple<int, int, int> sector = firstImgSectorsCompare[c % WidthSectors, c / HeightSectors];

                    for (int a = 0; a < secondImgSectorsCompare.Length; a++)
                    {
                        if (secondNumerList[a] == -1) continue;
                        int difference = ToUInt16(sector.Item1 - secondImgSectorsCompare[a % WidthSectors, a / HeightSectors].Item1) +
                            ToUInt16(sector.Item2 - secondImgSectorsCompare[a % WidthSectors, a / HeightSectors].Item2) +
                            ToUInt16(sector.Item3 - secondImgSectorsCompare[a % WidthSectors, a / HeightSectors].Item3);

                        if (difference < bestMatch)
                        {
                            secondImgSector = a;
                            firstImgSector = c;
                            bestMatch = difference;
                        }
                    }
                }

                //var test = new Rectangle(secondImgSector % WidthSectors * (firstImg.Width / WidthSectors), secondImgSector / HeightSectors * (firstImg.Height / HeightSectors), firstImg.Width / WidthSectors, firstImg.Height / HeightSectors);
                //var test2 = new Rectangle(firstImgSector % WidthSectors * (secondimage.Width / WidthSectors), firstImgSector / HeightSectors * (secondimage.Height / HeightSectors), secondimage.Width / WidthSectors, secondimage.Height / HeightSectors);
                g.DrawImage(secondimage, new Rectangle(secondImgSector % WidthSectors * (firstImg.Width / WidthSectors), secondImgSector / HeightSectors * (firstImg.Height / HeightSectors), firstImg.Width / WidthSectors, firstImg.Height / HeightSectors),
                    new Rectangle(firstImgSector % WidthSectors * (secondimage.Width / WidthSectors), firstImgSector / HeightSectors * (secondimage.Height / HeightSectors), secondimage.Width / WidthSectors, secondimage.Height / HeightSectors), GraphicsUnit.Pixel);
                pictureBox1.Image = image;
                pictureBox1.Update();

                firstNumerList[firstImgSector] = -1;
                secondNumerList[secondImgSector] = -1;

                matched.Add(bestMatch);
            }

            var leftover1 = firstNumerList.Where(n => n > -1).ToList().Count;
            var leftover2 = secondNumerList.Where(n => n > -1).ToList().Count;
            int under50 = matched.Where(m => m <= 50).ToList().Count;
            int over50 = matched.Where(m => m > 50).ToList().Count;

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

            double ratio = firstImg.Height * 1.0 / firstImg.Width;
            firstImg = CropAtRect(firstImg, new Rectangle(0, 0, 600, (int)(600 * ratio)));

            Thread makeSectors = new Thread(() => Prepimage(firstImg, true));
            makeSectors.Start();
        }

        private static Bitmap CropAtRect(Bitmap b, Rectangle r)
        {
            Bitmap nb = new Bitmap(r.Width, r.Height);
            using Graphics g = Graphics.FromImage(nb);
            g.DrawImage(b, -r.X, -r.Y, nb.Width, nb.Height);
            return nb;
        }
    }
}