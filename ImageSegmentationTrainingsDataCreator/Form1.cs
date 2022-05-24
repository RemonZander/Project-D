using System;
using System.IO;
using System.Collections.Generic;
using System.Drawing;
namespace ImageSegmentationTrainingsDataCreator
{
    public partial class Form1 : Form
    {
        const string backgrounds = @"../backgrounds/";

        public Form1()
        {
            InitializeComponent();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            folderBrowserDialog1.ShowDialog();

            if (string.IsNullOrEmpty(folderBrowserDialog1.SelectedPath)) return;

            string[] files = Directory.GetFiles(folderBrowserDialog1.SelectedPath);

            for (int a = 0; a < files.Length; a++)
            {
                Bitmap image = (Bitmap)Image.FromFile(files[a]);

                string[] backgroundFiles = Directory.GetFiles(backgrounds);

                Random random = new Random();
                int randomBackground = random.Next(0, backgroundFiles.Length);
                Bitmap currentBackground = new Bitmap(Image.FromFile(backgroundFiles[randomBackground]), new Size(250, 250));
                Graphics bg = Graphics.FromImage(currentBackground);
                (Bitmap image, int maxHeightObject, int maxWidthObject, int topOffset, int leftOffset) ObjectCutout = MakeMask(image, Color.FromArgb(0, 0, 0, 0), Color.FromArgb(0, 0, 0, 0), Color.FromArgb(0, 0, 0, 0), false);
                int newSize = random.Next(80, 128);
                ObjectCutout.image = new Bitmap(ObjectCutout.image, new Size(newSize, newSize));
                Graphics og = Graphics.FromImage(ObjectCutout.image);
                int xPos = random.Next(0, 250 - ObjectCutout.maxWidthObject + 20);
                int yPos = random.Next(0, 250 - ObjectCutout.maxHeightObject + 20);
                bg.DrawImage(ObjectCutout.image, xPos, yPos);
                bg.Save();

                currentBackground.Save("../test_data/" + a + ".jpg");

                currentBackground = new Bitmap(Image.FromFile(@"../Mask_background.jpg"));
                bg = Graphics.FromImage(currentBackground);
                bg.DrawImage(new Bitmap(Image.FromFile(files[a]), new Size(newSize, newSize)), xPos, yPos);
                bg.Save();
                Bitmap ObjectCutoutMask = MakeMask(currentBackground, Color.FromArgb(32, 143, 140), Color.FromArgb(68, 1, 84), Color.FromArgb(253, 231, 36), true).image;
                ObjectCutoutMask.Save("../test_data/" + a + " mask.jpg");
            }
        }

        private (Bitmap image, int maxHeightObject, int maxWidthObject, int topOffset, int leftOffset) MakeMask(Bitmap image, Color backgroundColor, Color objectColor, Color borderColor, bool colorObject)
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

                    if (color.R > 245 && color.G > 245 && color.B > 245)
                    {
                        image.SetPixel(a, b, backgroundColor);
                    }
                    else if (colorObject && color != borderColor && color != backgroundColor && color != Color.FromArgb(32, 142, 139))
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
    }
}