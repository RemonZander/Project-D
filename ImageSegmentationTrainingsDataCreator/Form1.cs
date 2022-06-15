using System;
using System.IO;
using System.Collections.Generic;
using System.Drawing;
using System.Threading;
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

            calc = new Thread(() => runThread());
            button1.Enabled = false;
            timer1.Enabled = true;
            calc.Start();
        }

        private void runThread()
        {
            string[] files = Directory.GetFiles(folderBrowserDialog1.SelectedPath);
            try
            {
                Directory.CreateDirectory(folderBrowserDialog1.SelectedPath + @"/.masks");
                Directory.CreateDirectory(folderBrowserDialog1.SelectedPath + @"/.data");
            }
            catch (Exception)
            {
            }
            BeginInvoke((MethodInvoker)delegate
            {
                progressBar1.Minimum = 0;
                progressBar1.Maximum = files.Length;
                progressBar1.Value = 0;
                label2.Text = "0 van de " + files.Length;
            });
            string[] backgroundFiles = Directory.GetFiles(backgrounds);
            Random random = new Random();

            for (int a = 0; a < files.Length; a++)
            {
                if (background)
                {
                    using Bitmap image = ResizeBitmap((Bitmap)Image.FromFile(files[a]), new Size(128, 128));
                    int randomBackground = random.Next(0, backgroundFiles.Length);
                    using Bitmap currentBackground = ResizeBitmap((Bitmap)Image.FromFile(backgroundFiles[randomBackground]), new Size(250, 250));

                    using Graphics bg = Graphics.FromImage(currentBackground);
                    (Bitmap image, int maxHeightObject, int maxWidthObject, int topOffset, int leftOffset) ObjectCutout = MakeCutout(image, Color.FromArgb(0, 0, 0, 0), Color.FromArgb(0, 0, 0, 0), Color.FromArgb(0, 0, 0, 0), false);
                    int newSize = random.Next(80, 128);
                    ObjectCutout.image = new Bitmap(ObjectCutout.image, new Size(newSize, newSize));
                    int xPos = random.Next(0, 250 - ObjectCutout.maxWidthObject + 20);
                    int yPos = random.Next(0, 250 - ObjectCutout.maxHeightObject + 20);
                    bg.DrawImage(ObjectCutout.image, xPos, yPos);
                    bg.Save();

                    currentBackground.Save(folderBrowserDialog1.SelectedPath + @"/.data/" + files[a].Replace(folderBrowserDialog1.SelectedPath, ""));

                    using Bitmap currentBackgroundNew = (Bitmap)Image.FromFile(@"../Mask_background.jpg");
                    using Graphics bg2 = Graphics.FromImage(currentBackgroundNew);
                    using Bitmap mask = makeMask(ObjectCutout.image, Color.FromArgb(68, 1, 84), Color.FromArgb(32, 143, 140));
                    bg2.DrawImage(mask, xPos, yPos);
                    bg2.Save();
                    currentBackgroundNew.Save(folderBrowserDialog1.SelectedPath + @"/.masks/" + files[a].Replace(folderBrowserDialog1.SelectedPath, ""));
                }
                else
                {
                    File.Copy(files[a], folderBrowserDialog1.SelectedPath + @"/.data/" + files[a].Replace(folderBrowserDialog1.SelectedPath, ""));

                    using Bitmap maskImage = (Bitmap)Image.FromFile(files[a]);
                    using Bitmap mask = makeMask(maskImage, Color.FromArgb(68, 1, 84), Color.FromArgb(32, 143, 140));
                    mask.Save(folderBrowserDialog1.SelectedPath + @"/.masks/" + files[a].Replace(folderBrowserDialog1.SelectedPath, ""));
                }

                BeginInvoke((MethodInvoker)delegate
                {
                    progressBar1.Value += 1;
                    progressBar1.Update();
                    label2.Text = a + 1 + " van de " + files.Length;
                    label2.Update();
                    Update();
                });
            }

            MessageBox.Show("Klaar!");
        }

        private Bitmap makeMask(Bitmap cutout, Color backgroundColor, Color objectColor)
        {
            //using (cutout)
            for (int a = 0; a < cutout.Width; a++)
            {
                for (int b = 0; b < cutout.Height; b++)
                {
                    Color pixelColor = cutout.GetPixel(a, b);
                    if (pixelColor.A > 0 && background)
                    {
                        cutout.SetPixel(a, b, backgroundColor);
                        continue;
                    }
                    else if (pixelColor.R > 245 && pixelColor.G > 245 && pixelColor.B > 245 && !background)
                    {
                        cutout.SetPixel(a, b, backgroundColor);
                        continue;
                    }

                        cutout.SetPixel(a, b, objectColor);
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
                   /* else if (colorObject && color != borderColor && color != backgroundColor && color != Color.FromArgb(32, 142, 139))
                    {
                        if (a < 249 && a > 0)
                        {
                            Color pixelRight = image.GetPixel(a + 1, b);
                            if ((pixelRight.R > 245 && pixelRight.G > 245 && pixelRight.B > 245) || pixelRight == backgroundColor || pixelRight == Color.FromArgb(32, 142, 139))
                            {
                                try
                                {
                                    image.SetPixel(a, b, borderColor);
                                    image.SetPixel(a + 1, b, borderColor);
                                    image.SetPixel(a + 2, b, borderColor);
                                    image.SetPixel(a + 3, b, borderColor);
                                    image.SetPixel(a + 4, b, borderColor);

                                }
                                catch (Exception)
                                {
                                }
                                continue;
                            }

                            Color pixelLeft = image.GetPixel(a - 1, b);
                            if ((pixelLeft.R > 245 && pixelLeft.G > 245 && pixelLeft.B > 245) || pixelLeft == backgroundColor || pixelLeft == Color.FromArgb(32, 142, 139))
                            {
                                try
                                {
                                    image.SetPixel(a, b, borderColor);
                                    image.SetPixel(a - 1, b, borderColor);
                                    image.SetPixel(a - 2, b, borderColor);
                                    image.SetPixel(a - 3, b, borderColor);
                                    image.SetPixel(a - 4, b, borderColor);

                                }
                                catch (Exception)
                                {
                                }
                                continue;
                            }
                        }

                        if (b < 249 && b > 0)
                        {
                            
                            Color pixelUnder = image.GetPixel(a, b + 1);
                            if ((pixelUnder.R > 245 && pixelUnder.G > 245 && pixelUnder.B > 245) || pixelUnder == backgroundColor || pixelUnder == Color.FromArgb(32, 142, 139))
                            {
                                try
                                {
                                    image.SetPixel(a, b, borderColor);
                                    image.SetPixel(a, b + 1, borderColor);
                                    image.SetPixel(a, b + 2, borderColor);
                                    image.SetPixel(a, b + 3, borderColor);
                                    image.SetPixel(a, b + 4, borderColor);

                                }
                                catch (Exception)
                                {
                                }
                                continue;
                            }

                            Color pixelAbove = image.GetPixel(a, b - 1);
                            if ((pixelAbove.R > 245 && pixelAbove.G > 245 && pixelAbove.B > 245) || pixelAbove == backgroundColor || pixelAbove == Color.FromArgb(32, 142, 139))
                            {
                                try
                                {
                                    image.SetPixel(a, b, borderColor);
                                    image.SetPixel(a, b - 1, borderColor);
                                    image.SetPixel(a, b - 2, borderColor);
                                    image.SetPixel(a, b - 3, borderColor);
                                    image.SetPixel(a, b - 4, borderColor);

                                }
                                catch (Exception)
                                {
                                }
                                continue;
                            }
                        }
                        image.SetPixel(a, b, objectColor);
                    }*/
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