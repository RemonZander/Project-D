using System.IO;
using System.Text;
namespace Exif_test_project
{
    public partial class Form1 : Form
    {
        private byte[] byteArray = new byte[1];

        public Form1()
        {
            InitializeComponent();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            openFileDialog1.ShowDialog();
            if (string.IsNullOrEmpty(openFileDialog1.SafeFileName) || openFileDialog1.SafeFileName.Contains("openFi")) return;

            textBox1.Text = openFileDialog1.SafeFileName;
            textBox2.Enabled = true;
            textBox3.Enabled = true;
            textBox4.Enabled = true;
            button2.Enabled = true;
        }

        private void button2_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrEmpty(textBox2.Text))
            {
                MessageBox.Show("Je moet een productnaam invullen");
                return;
            }
            if (string.IsNullOrEmpty(textBox3.Text))
            {
                MessageBox.Show("Je moet een hoofdcategorie invullen");
                return;
            }
            if (string.IsNullOrEmpty(textBox4.Text))
            {
                MessageBox.Show("Je moet een subcategorie invullen");
                return;
            }

            //Convert textboxes to bytearray and add 0 where needed
            byte[] titleTemp = ASCIIEncoding.ASCII.GetBytes(textBox2.Text);     //max supported title length is 127 min supported length is 2
            byte[] mainCategoryTemp = ASCIIEncoding.ASCII.GetBytes(textBox3.Text);      //max supported maincategory length is 127    min supported length is 2
            byte[] subCategories = ASCIIEncoding.ASCII.GetBytes(textBox4.Text);         //max supported length is 255 min supported length is 2
            Array.Resize(ref subCategories, subCategories.Length + 1);

            byte[] title = new byte[titleTemp.Length * 2];      
            for (int a = 0; a < title.Length; a+= 2)
            {
                title[a] = titleTemp[a / 2];
                title[a + 1] = 0;
            }
            Array.Resize(ref title, title.Length + 2);              //add 2 because the title has 2 trailing 00 00 at the end

            byte[] mainCategory = new byte[mainCategoryTemp.Length * 2];       
            for (int a = 0; a < mainCategory.Length; a += 2)
            {
                mainCategory[a] = mainCategoryTemp[a / 2];
                mainCategory[a + 1] = 0;
            }
            Array.Resize(ref mainCategory, mainCategory.Length + 3);              //add 3 because the maincategory has 3 trailing 00 00 at the end

            //Find end of exif data and copy image data into new byte array
            byteArray = File.ReadAllBytes(openFileDialog1.FileName);
            int exifEnd = EndExifIndex(2);
            byte[] image = new byte[byteArray.Length - exifEnd];
            Array.Copy(byteArray, exifEnd, image, 0, byteArray.Length - exifEnd);

            //build new exif data
            string mainCategoryPos = ToHex(62 + title.Length - 3 - 9, "");
            string exifPointer = ToHex(60 + title.Length + mainCategory.Length + 1 - 12, "");
            string subCategoryPos = ToHex(62 + title.Length + mainCategory.Length + 29 - 12, "");
            string totalLength = ToHex(58 + title.Length + mainCategory.Length + 37 + subCategories.Length, "");
            byte[] newByteArray = new byte[62] {255, 216, 255, 225,
                Convert.ToByte(totalLength.Length > 2 ? ToInt(totalLength[..(totalLength.Length / 2)], 0, 0) : 0),
                Convert.ToByte(totalLength.Length > 2 ? ToInt(totalLength[(totalLength.Length / 2)..], 0, 0) : ToInt(totalLength, 0, 0)),
                69, 120, 105, 102, 0, 0, 77, 77, 0, 42, 0, 0, 0, 8, 0, 7, 135, 105, 0, 4, 0, 0, 0, 1, 0, 0,
                Convert.ToByte(exifPointer.Length > 2 ? ToInt(exifPointer[..(exifPointer.Length / 2)], 0, 0) : 0),
                Convert.ToByte(exifPointer.Length > 2 ? ToInt(exifPointer[(exifPointer.Length / 2)..], 0, 0) : ToInt(exifPointer, 0, 0)), 
                156, 155, 0, 1, 0, 0, 0, 
                Convert.ToByte(title.Length), 0, 0, 0, 50, 156, 159, 0, 1, 0, 0, 0, Convert.ToByte(mainCategory.Length - 1), 0, 0,
                Convert.ToByte(mainCategoryPos.Length > 2 ? ToInt(mainCategoryPos[..(mainCategoryPos.Length / 2)], 0, 0) : 0),    //if position of maincategory is more than 255 or FF in hex then calculate the value for the second byte.
                Convert.ToByte(mainCategoryPos.Length > 2 ? ToInt(mainCategoryPos[(mainCategoryPos.Length / 2)..], 0, 0) : ToInt(mainCategoryPos, 0, 0)), 0, 0,   //first byte of maincategory data position. If 2 byte's is needed only calculate the byte value for the first 2 hex values
            0, 1}.Concat(title).ToArray();
            newByteArray = newByteArray.Concat(mainCategory).ToArray();
            newByteArray = newByteArray.Concat(new byte[37] {3, 146, 134, 0, 7, 0, 0, 0, Convert.ToByte(subCategories.Length + 7), 0, 0,
                Convert.ToByte(subCategoryPos.Length > 2 ? ToInt(subCategoryPos[..(subCategoryPos.Length / 2)], 0, 0) : 0),
                Convert.ToByte(subCategoryPos.Length > 2 ? ToInt(subCategoryPos[(subCategoryPos.Length / 2)..], 0, 0) : ToInt(subCategoryPos, 0, 0)), 
                160, 0, 0, 7, 0, 0, 0, 4, 48, 49, 48, 48, 0, 0, 0, 0, 65, 83, 67, 73, 73, 0, 0, 0}).ToArray();
            newByteArray = newByteArray.Concat(subCategories).ToArray();
            byteArray = newByteArray.Concat(image).ToArray();

            saveFileDialog1.ShowDialog();
        }

        /// <summary>
        /// This iterative  function finds the first occurrence of FF DB wich is the end of exif identifier in jpeg files
        /// </summary>
        /// <param name="startIndex">This should be 2 when you call the function</param>
        /// <returns></returns>
        private int EndExifIndex(int startIndex)
        {
            return byteArray[startIndex] == 255 && byteArray[startIndex + 1] == 219 ? startIndex : 
                EndExifIndex(startIndex + ToInt(ToHex(byteArray[startIndex + 2], "") + ToHex(byteArray[startIndex + 3], ""), 0, 0) + 2);
        }

        /// <summary>
        /// Convert any hex string to the corresponding base 10 number
        /// </summary>
        /// <param name="hex">This should be the hex string you want to convert</param>
        /// <param name="value">This should be empty on function call. This is used to build the value</param>
        /// <param name="pos">This should be empty on function call. This is used to keep track of the position in the hex string</param>
        /// <returns></returns>
        private int ToInt(string hex, int value, int pos)
        {
            if (pos == hex.Length) return value;
            return hex[pos] switch
            {
                'A' => ToInt(hex, value + 10 * Convert.ToInt32(Math.Pow(16, hex.Length - (pos + 1))), pos +=1),
                'B' => ToInt(hex, value + 11 * Convert.ToInt32(Math.Pow(16, hex.Length - (pos + 1))), pos += 1),
                'C' => ToInt(hex, value + 12 * Convert.ToInt32(Math.Pow(16, hex.Length - (pos + 1))), pos += 1),
                'D' => ToInt(hex, value + 13 * Convert.ToInt32(Math.Pow(16, hex.Length - (pos + 1))), pos += 1),
                'E' => ToInt(hex, value + 14 * Convert.ToInt32(Math.Pow(16, hex.Length - (pos + 1))), pos += 1),
                'F' => ToInt(hex, value + 15 * Convert.ToInt32(Math.Pow(16, hex.Length - (pos + 1))), pos += 1),
                _ => ToInt(hex, value + Convert.ToInt32(hex[pos].ToString()) * Convert.ToInt32(Math.Pow(16, hex.Length - (pos + 1))), pos += 1),
            };
        }

        /// <summary>
        /// Convert any base 10 number to a hex string
        /// </summary>
        /// <param name="value">This should be the base 10 number</param>
        /// <param name="hex">This should be ampty on function call. This is used to build the hex value</param>
        /// <returns></returns>
        private string ToHex(int value, string hex)
        {
            if (value == 0) return hex;

            return (value % 16) switch
            {
                10 => ToHex(value / 16, "A" + hex),
                11 => ToHex(value / 16, "B" + hex),
                12 => ToHex(value / 16, "C" + hex),
                13 => ToHex(value / 16, "D" + hex),
                14 => ToHex(value / 16, "E" + hex),
                15 => ToHex(value / 16, "F" + hex),
                0 => value == 0 ? "0" + hex : ToHex(value / 16, "0" + hex),
                _ => ToHex(value / 16, value % 16 + hex),
            };
        }

        private void saveFileDialog1_FileOk(object sender, System.ComponentModel.CancelEventArgs e)
        {
            File.WriteAllBytes(saveFileDialog1.FileName, byteArray);
            MessageBox.Show("Bestand opgeslagen!");
        }
    }
}
