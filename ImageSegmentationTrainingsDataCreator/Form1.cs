using System;
using System.IO;
using System.Collections.Generic;
using System.Drawing;
using System.Threading;
using System.Drawing.Imaging;
namespace ImageSegmentationTrainingsDataCreator
{
    public partial class Form1 : Form
    {
        const string backgrounds = @"C:\Users\remon\Desktop\backgrounds\";
        Thread calc;
        bool background;

        public Form1()
        {
            InitializeComponent();
        }

        private Bitmap ResizeBitmap(Bitmap original, Size size)
        {
            using (original)
            return new Bitmap(original, size);
        }

        private void button1_Click(object sender, EventArgs e)
        {
            folderBrowserDialog1.ShowDialog();

            if (string.IsNullOrEmpty(folderBrowserDialog1.SelectedPath)) return;

            calc = new Thread(() => RunThread());
            button1.Enabled = false;
            timer1.Enabled = true;
            calc.Start();
        }

        private void RunThread()
        {
            string[] files = Directory.GetFiles(folderBrowserDialog1.SelectedPath);
            BeginInvoke((MethodInvoker)delegate
            {
                progressBar1.Minimum = 0;
                progressBar1.Maximum = files.Length;
                progressBar1.Value = 0;
                label2.Text = "0 van de " + files.Length + " afbeeldingen";
            });
            string[] backgroundFiles = Directory.GetFiles(backgrounds);
            Random random = new Random();

            using StreamWriter trainFile = File.CreateText(folderBrowserDialog1.SelectedPath + "/train.txt");
            using StreamWriter testFile = File.CreateText(folderBrowserDialog1.SelectedPath + "/test.txt");
            int testCount = 0;
            int offset = Convert.ToInt32(textBox3.Text);
            for (int a = offset; a < (files.Length + offset); a++)
            {
                if (background)
                {
                    using Bitmap image = ResizeBitmap((Bitmap)Image.FromFile(files[a]), new Size(128, 128));
                    int randomBackground = random.Next(0, backgroundFiles.Length);
                    using Bitmap currentBackground = ResizeBitmap((Bitmap)Image.FromFile(backgroundFiles[randomBackground]), new Size(250, 250));

                    using Graphics bg = Graphics.FromImage(currentBackground);
                    bg.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.NearestNeighbor;
                    (Bitmap image, int maxHeightObject, int maxWidthObject, int topOffset, int leftOffset) ObjectCutout = MakeCutout(image, Color.FromArgb(0, 0, 0, 0), Color.FromArgb(0, 0, 0, 0), Color.FromArgb(0, 0, 0, 0), false);
                    int newSize = random.Next(80, 128);
                    ObjectCutout.image = new Bitmap(ObjectCutout.image, new Size(newSize, newSize));
                    int xPos = random.Next(0, 250 - ObjectCutout.maxWidthObject + 20);
                    int yPos = random.Next(0, 250 - ObjectCutout.maxHeightObject + 20);
                    bg.DrawImage(ObjectCutout.image, xPos, yPos);
                    bg.Save();

                    currentBackground.Save(@"C:\Users\remon\Desktop\images\" + textBox1.Text + a + ".png", ImageFormat.Png);
                    if ((a - offset) % 2 == 0 && testCount < 2000)
                    {
                        testFile.WriteLine(textBox1.Text + a + " " + textBox2.Text);
                        testCount += 1;
                    }
                    else
                    {
                        trainFile.WriteLine(textBox1.Text + a + " " + textBox2.Text);
                    }

                    using Bitmap currentBackgroundNew = (Bitmap)Image.FromFile(@"../Mask_background.jpg");
                    using Graphics bg2 = Graphics.FromImage(currentBackgroundNew);
                    bg2.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.NearestNeighbor;
                    using Bitmap mask = makeMask(ObjectCutout.image, Color.FromArgb(1, 1, 1), Color.FromArgb(2, 2, 2));
                    bg2.DrawImage(mask, xPos, yPos);
                    bg2.Save();
                    currentBackgroundNew.Save(@"C:\Users\remon\Desktop\masks\" + textBox1.Text + a + ".png", ImageFormat.Png);
                }
                else
                {
                    using Bitmap image = (Bitmap)Image.FromFile(files[a - offset]);
                    image.Save(@"C:\Users\remon\Desktop\images\" + textBox1.Text + a + ".png", ImageFormat.Png);

                    using Bitmap maskImage = (Bitmap)Image.FromFile(files[a - offset]);
                    using Bitmap mask = makeMask(maskImage, Color.FromArgb(1, 1, 1), Color.FromArgb(2, 2, 2));
                    mask.Save(@"C:\Users\remon\Desktop\masks\" + textBox1.Text + a + ".png", ImageFormat.Png);

                    if ((a - offset) % 2 == 0 && testCount < 2000)
                    {
                        testFile.WriteLine(textBox1.Text + a + " " + textBox2.Text);
                        testCount += 1;
                    }
                    else
                    {
                        trainFile.WriteLine(textBox1.Text + a + " " + textBox2.Text);
                    }
                }

                BeginInvoke((MethodInvoker)delegate
                {
                    progressBar1.Value += 1;
                    progressBar1.Update();
                    label2.Text = a - offset + 1 + " van de " + files.Length + " afbeeldingen";
                    label2.Update();
                    Update();
                });
            }

            MessageBox.Show("Klaar!");
        }

        private Bitmap makeMask(Bitmap cutout, Color backgroundColor, Color objectColor)
        {
            for (int a = 0; a < cutout.Width; a++)
            {
                for (int b = 0; b < cutout.Height; b++)
                {
                    Color pixelColor = cutout.GetPixel(a, b);
                    if (pixelColor.A > 0 && background)
                    {
                        cutout.SetPixel(a, b, objectColor);
                        continue;
                    }
                    else if (pixelColor.R > 245 && pixelColor.G > 245 && pixelColor.B > 245 && !background)
                    {
                        cutout.SetPixel(a, b, objectColor);
                        continue;
                    }

                    cutout.SetPixel(a, b, backgroundColor);
                }
            }
            return cutout;
        }

        private (Bitmap image, int maxHeightObject, int maxWidthObject, int topOffset, int leftOffset) MakeCutout(Bitmap image, Color backgroundColor, Color objectColor, Color borderColor, bool colorObject)
        {
            int leftOffset = 128;
            int topOffset = 128;
            int maxWidthObject = 0;
            int maxHeightObject = 0;
            for (int a = 0; a < image.Height; a++)
            {
                for (int b = 0; b < image.Width; b++)
                {
                    Color color = image.GetPixel(a, b);

                    if ((color.R > 245 && color.G > 245 && color.B > 245) || (a >= 240 && b >= 208))
                    {
                        image.SetPixel(a, b, backgroundColor);
                    }
                    else
                    {
                        if (a < leftOffset) leftOffset = a;
                        if (a > maxWidthObject) maxWidthObject = a;
                        if (b > maxHeightObject) maxHeightObject = b;
                        if (b < topOffset) topOffset = b;
                    }
                }
            }
            image.MakeTransparent(Color.FromArgb(0, 0, 0, 0));
            return (image, maxHeightObject, maxWidthObject, topOffset, leftOffset);
        }

        private void label2_Click(object sender, EventArgs e)
        {

        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            if (calc.ThreadState == ThreadState.Stopped)
            {
                button1.Enabled = true;
                timer1.Enabled = false;
            }
        }

        private void checkBox1_CheckedChanged(object sender, EventArgs e)
        {
            if (checkBox1.Checked)
            {
                background = true;
            }
            else
            {
                background = false;
            }
        }
    }
}